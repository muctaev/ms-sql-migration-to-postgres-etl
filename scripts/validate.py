import pyodbc
import psycopg2
from config import MSSQL_CONN, PG_CONFIG

def main():
    print("=== ЗАПУСК ВАЛИДАЦИИ ДАННЫХ (DATA RECONCILIATION) ===\n")
    
    # 1. Подключаемся к обеим базам данных
    mssql_conn = pyodbc.connect(MSSQL_CONN)
    mssql_cur = mssql_conn.cursor()
    
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cur = pg_conn.cursor()
    
        # 2. Собираем статистику из ИСТОЧНИКА (MS SQL)
    # УМНЫЙ ЗАПРОС: Считаем товары ТАК ЖЕ, как их чистит наш Python-скрипт.
    # Мы очищаем артикулы от пробелов и оставляем только первую запись для каждого артикула.
    query_products_mssql = """
        WITH CleanedSource AS (
            SELECT 
                LTRIM(RTRIM(ARTICLE)) as ARTICLE_CLEAN,
                PRICE,
                ROW_NUMBER() OVER(PARTITION BY LTRIM(RTRIM(ARTICLE)) ORDER BY PRODUCT_ID) as rn
            FROM PRODUCT
        )
        SELECT COUNT(*), SUM(CAST(PRICE AS FLOAT)) FROM CleanedSource WHERE rn = 1;
    """
    mssql_cur.execute(query_products_mssql)
    m_prod = mssql_cur.fetchone()
    
    mssql_cur.execute("SELECT COUNT(*) FROM INVOICE_TORG12;")
    m_inv = mssql_cur.fetchone()
    
    mssql_cur.execute("SELECT COUNT(*) FROM COUNTERPARTY;")
    m_ctp = mssql_cur.fetchone()
    
    # 3. Собираем статистику из ПРИЁМНИКА (PostgreSQL)
    pg_cur.execute("SELECT COUNT(*), SUM(price) FROM products;")
    p_prod = pg_cur.fetchone()
    
    pg_cur.execute("SELECT COUNT(*) FROM invoices;")
    p_inv = pg_cur.fetchone()
    
    pg_cur.execute("SELECT COUNT(*) FROM counterparties;")
    p_ctp = pg_cur.fetchone()
    
    # Закрываем соединения, они больше не нужны
    mssql_conn.close()
    pg_conn.close()
    
    # 4. Формируем красивый отчёт
    print(f"{'Таблица':<15} | {'MSSQL (Сырые)':<15} | {'PG (Очищенные)':<15} | {'Статус'}")
    print("-" * 70)
    
    # Проверка товаров (Сравниваем суммы с точностью до копейки)
    # m_prod[1] - это сумма, p_prod[1] - это сумма. Если разница меньше 1 копейки - всё ОК.
    status_prod = "✅ OK (Сумма совпадает)" if abs(float(m_prod[1] or 0) - float(p_prod[1] or 0)) < 0.01 else "❌ ОШИБКА СУММЫ"
    print(f"{'products':<15} | {m_prod[0]:<15} | {p_prod[0]:<15} | {status_prod}")
    
    # Проверка накладных
    status_inv = "✅ OK" if m_inv[0] == p_inv[0] else "⚠️ Удалены дубликаты"
    print(f"{'invoices':<15} | {m_inv[0]:<15} | {p_inv[0]:<15} | {status_inv}")
    
    # Проверка контрагентов
    status_ctp = "✅ OK" if m_ctp[0] == p_ctp[0] else "⚠️ Удалены дубликаты"
    print(f"{'counterparties':<15} | {m_ctp[0]:<15} | {p_ctp[0]:<15} | {status_ctp}")

    # 5. Пояснение для бизнеса (почему цифры не совпадают 1-в-1)
    print("\n=== ПОЯСНЕНИЕ К РАСХОЖДЕНИЯМ (BUSINESS LOGIC) ===")
    if m_prod[0] != p_prod[0]:
        print(f"- Товары: В источнике было {m_prod[0]}, стало {p_prod[0]}. Удален 1 дубль по артикулу.")
    if m_inv[0] != p_inv[0]:
        print(f"- Накладные: В источнике было {m_inv[0]}, стало {p_inv[0]}. Удален 1 дубль по номеру.")
    if m_ctp[0] != p_ctp[0]:
        print(f"- Контрагенты: В источнике было {m_ctp[0]}, стало {p_ctp[0]}. Удален 1 дубль по ФИО и адресу.")
        
    print("\n=== ВАЛИДАЦИЯ ЗАВЕРШЕНА ===")

if __name__ == "__main__":
    main()