import psycopg2
import psycopg2.extras
import pandas as pd
import warnings
from config import PG_CONFIG

# Импортируем функции извлечения и очистки из прошлого файла, чтобы не копировать код
from transform import extract_data, clean_products, clean_invoices, clean_counterparties

warnings.filterwarnings('ignore')

def load_to_postgres(df, table_name, columns, conflict_column, pg_conn):
    """
    Универсальная функция UPSERT.
    Если записи нет — она вставляется (INSERT).
    Если запись с таким conflict_column уже есть — она обновляется (UPDATE).
    """
    # Формируем SQL-шаблон. %s здесь — это место, куда psycopg2 безопасно подставит массив данных
    insert_query = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES %s
        ON CONFLICT ({conflict_column}) 
        DO UPDATE SET 
        {", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != conflict_column])};
    """
    
    # Превращаем DataFrame в список кортежей. 
    # ВАЖНО: Заменяем pandas-пустоту NaT (в датах) на классический Python-овский None, 
    # чтобы PostgreSQL понял это как SQL NULL.
    df_clean_for_db = df[columns].replace({pd.NaT: None})
    data_tuples = [tuple(x) for x in df_clean_for_db.to_numpy()]
    
    # execute_values — это сверхбыстрый способ загрузить тысячи строк одним пакетом
    with pg_conn.cursor() as cursor:
        psycopg2.extras.execute_values(cursor, insert_query, data_tuples)
    pg_conn.commit()
    print(f"-> Таблица '{table_name}' успешно загружена ({len(df)} строк).")

def main():
    print("=== ЭТАП ЗАГРУЗКИ (LOAD) ===")
    
    # 1. Забираем и чистим данные (используем наработки Сессии 5)
    df_products, df_invoices, df_counterparties = extract_data()
    df_products_clean = clean_products(df_products)
    df_invoices_clean = clean_invoices(df_invoices)
    df_counterparties_clean = clean_counterparties(df_counterparties)
    
    # 2. ИСПРАВЛЕНИЕ РЕГИСТРА КОЛОНОК (Наш новый код!)
    # MS SQL отдает названия колонок в ВЕРХНЕМ регистре (PRODUCT_ID), 
    # а PostgreSQL и наш скрипт ожидают их в нижнем (product_id).
    # Приводим все названия к нижнему регистру одной командой.
    df_products_clean.columns = df_products_clean.columns.str.lower()
    df_invoices_clean.columns = df_invoices_clean.columns.str.lower()
    df_counterparties_clean.columns = df_counterparties_clean.columns.str.lower()
    
    # 3. Подключаемся к PostgreSQL
    print("Подключаемся к PostgreSQL...")
    pg_conn = psycopg2.connect(**PG_CONFIG)
    
    # 4. Загружаем таблицы по очереди
    load_to_postgres(
        df_counterparties_clean, 
        'counterparties', 
        ['ctp_id', 'full_name', 'phone', 'address'], 
        'ctp_id', 
        pg_conn
    )
    
    load_to_postgres(
        df_products_clean, 
        'products', 
        ['product_id', 'article', 'product_name', 'barcode', 'unit_name', 'unit_code', 'price'], 
        'product_id', 
        pg_conn
    )
    
    load_to_postgres(
        df_invoices_clean, 
        'invoices', 
        ['invoice_id', 'invoice_number', 'invoice_date', 'comment'], 
        'invoice_id', 
        pg_conn
    )
    
    pg_conn.close()
    print("\n=== ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО ===")

if __name__ == "__main__":
    main()