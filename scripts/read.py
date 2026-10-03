# Импортируем наши "инструменты"
import pyodbc
import pandas as pd
# Импортируем настройки из соседнего файла config.py
from config import MSSQL_CONN 

def main():
    print("1. Подключаемся к MS SQL Server...")
    # Устанавливаем соединение (курьер показывает пропуск на проходной)
    conn = pyodbc.connect(MSSQL_CONN)
    
    print("2. Читаем таблицу PRODUCT...")
    # Пишем SQL-запрос, который хотим выполнить
    query = "SELECT * FROM PRODUCT;"
    
    # Отправляем запрос и сразу складываем результат в "тележку" pandas (DataFrame)
    df_product = pd.read_sql(query, conn)
    
    # Обязательно закрываем соединение, чтобы не "зависнуть" на сервере
    conn.close()
    
    print("\n--- Первые 5 строк из таблицы PRODUCT ---")
    # Метод .head() показывает только первые 5 строк, чтобы не засорять экран
    print(df_product.head())
    
    print(f"\nВсего строк привезено со склада: {len(df_product)}")

# Эта конструкция означает: "Запусти функцию main, только если файл запущен напрямую"
if __name__ == "__main__":
    main()