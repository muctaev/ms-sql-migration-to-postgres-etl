import pyodbc
import pandas as pd
import warnings # 1. Импортируем библиотеку для управления системными сообщениями
from config import MSSQL_CONN

# 2. Говорим pandas игнорировать предупреждения (Warnings), чтобы консоль была чистой
warnings.filterwarnings('ignore')

def extract_data():
    """Функция забирает все три нужные таблицы из MS SQL"""
    conn = pyodbc.connect(MSSQL_CONN)
    # 3. Добавляем .copy() в конце. Это создает независимую копию данных в памяти, 
    # чтобы pandas перестал выдавать SettingWithCopyWarning при изменении колонок.
    df_products = pd.read_sql("SELECT * FROM PRODUCT;", conn).copy()
    df_invoices = pd.read_sql("SELECT * FROM INVOICE_TORG12;", conn).copy()
    df_counterparties = pd.read_sql("SELECT * FROM COUNTERPARTY;", conn).copy()
    conn.close()
    return df_products, df_invoices, df_counterparties

def clean_products(df):
    print("-> Чистим товары...")
    df['ARTICLE'] = df['ARTICLE'].str.strip()
    df['PRODUCT_NAME'] = df['PRODUCT_NAME'].str.strip()
    df = df.drop_duplicates(subset=['ARTICLE'], keep='first')
    return df

def clean_invoices(df):
    print("-> Чистим накладные...")
    df = df.drop_duplicates(subset=['INVOICE_NUMBER'], keep='first')
    
    # 4. ИСПРАВЛЕНИЕ ДАТ:
    # format='mixed' — это магия pandas (доступна в версиях 2.0+). 
    # Она говорит: "У меня тут винегрет из форматов, распознай каждый сам".
    # dayfirst=True помогает понять, что в "02.10.2023" двойка — это день, а не месяц.
    df['INVOICE_DATE'] = pd.to_datetime(df['INVOICE_DATE'], errors='coerce', format='mixed', dayfirst=True)
    
    df['COMMENT'] = df['COMMENT'].replace('', None)
    return df

def clean_counterparties(df):
    print("-> Чистим контрагентов...")
    df = df.drop_duplicates(subset=['FULL_NAME', 'ADDRESS'], keep='first')
    df['PHONE'] = df['PHONE'].str.replace(r'\D', '', regex=True)
    df.loc[df['PHONE'] == '', 'PHONE'] = None
    return df

def main():
    print("=== НАЧАЛО ТРАНСФОРМАЦИИ ===")
    df_products, df_invoices, df_counterparties = extract_data()
    
    print(f"Сырых товаров: {len(df_products)} | Накладных: {len(df_invoices)} | Контрагентов: {len(df_counterparties)}")
    
    df_products_clean = clean_products(df_products)
    df_invoices_clean = clean_invoices(df_invoices)
    df_counterparties_clean = clean_counterparties(df_counterparties)
    
    print("\n=== РЕЗУЛЬТАТ ОЧИСТКИ ===")
    print(f"Чистых товаров: {len(df_products_clean)}")
    print(f"Чистых накладных: {len(df_invoices_clean)}")
    print(f"Чистых контрагентов: {len(df_counterparties_clean)}")
    
    print("\nПроверка дат:")
    print(df_invoices_clean[['INVOICE_NUMBER', 'INVOICE_DATE']])

if __name__ == "__main__":
    main()