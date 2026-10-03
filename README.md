# MS SQL Server to PostgreSQL ETL Pipeline

Proof-of-concept проекта по миграции данных из реляционной Базы данных MS SQL Server в PostgreSQL с использованием Python (Pandas). Проект включает полный цикл: извлечение (Extract), очистку и трансформацию (Transform), загрузку с идемпотентным UPSERT (Load), а также модуль валидации данных и бизнес-аналитику.

## Стек технологий

- **Языки:** Python 3.x, SQL (MS SQL, PostgreSQL)
- **Библиотеки:** pandas, pyodbc, psycopg2
- **Инструменты:** pgAdmin, SQL Server Management Studio, Git

## Архитектура проекта

- **scripts/** — Python-скрипты пайплайна:
   - read.py — извлечение данных из источника.
   - transform.py — очистка дат, дедупликация, нормализация строк.
   - load.py — загрузка в PostgreSQL через паттерн UPSERT (ON CONFLICT).
   - validate.py — сверка контрольных сумм (Data Reconciliation) между источниками.
- **sql/** — DDL-схемы целевой БД и сложные аналитические запросы (оконные функции, CTE).
- **config_example.py** — шаблон настроек для подключения к БД.

## Особенности этапа трансформации (Data Cleaning)

- Парсинг смешанных форматов дат (DD.MM.YYYY, YYYY/MM/DD) с использованием format='mixed'.
- Удаление бизнес-дубликатов по уникальным ключам.
- Очистка телефонных номеров и артикулов от мусорных символов.
- Обработка пропусков (замена невалидных значений на NULL/NaT).

## Валидация данных (Data Quality)

Реализован скрипт validate.py, который автоматически сверяет количество строк и контрольные суммы (SUM) между источником и приёмником, учитывая бизнес-логику дедупликации.

## Аналитика в PostgreSQL

В папке sql/ представлены запросы уровня Middle:

1.  analytics_seasonality.sql — расчёт динамики выставления накладных месяц к месяцу (MoM) с использованием CTE и LAG().
2.  analytics_pricing.sql — автоматическое ценовое сегментирование товаров с помощью NTILE().
3.  analytics_anomalies.sql — поиск аномальных дней с помощью COUNT() OVER(PARTITION BY ...).

## Как запустить проект локально

1.  Клонируйте репозиторий: git clone https://github.com/muctaev/ms-sql-migration-to-postgres-etl.git
2.  Создайте виртуальное окружение: python -m venv venv и активируйте его: venv**SScripts**Sactivate
3.  Установите зависимости: pip install pyodbc psycopg2-binary pandas
4.  Скопируйте config_example.py в config.py и заполните своими паролями.
5.  Запустите этапы по очереди: python scripts/load.py, затем python scripts/validate.py.

---

**Автор:** Ramil Mustaev | Проект создан в учебных целях для личного портфолио.
