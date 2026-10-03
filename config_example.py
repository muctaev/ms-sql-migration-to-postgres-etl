# Фвйл-шаблон! Скопируйте этот файл в config.py и заполните своими данными.

MSSQL_CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=ВашСервер;"
    "DATABASE=ВашаБазаДанных;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

PG_CONFIG = {
    "dbname": "ВашаВазаДанных",
    "user": "ВашПользователь",
    "password": "ВашПароль",
    "host": "localhost",
    "port": "5432"
}