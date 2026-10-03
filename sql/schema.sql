-- Создание таблицы контрагентов
CREATE TABLE counterparties (
    ctp_id INTEGER PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    address VARCHAR(250) NOT NULL
);

-- Создание таблицы товаров
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    article VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    barcode VARCHAR(50),
    unit_name VARCHAR(20) NOT NULL,
    unit_code VARCHAR(10),
    price NUMERIC(19, 4)
);

-- Создание таблицы накладных
CREATE TABLE invoices (
    invoice_id INTEGER PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE,
    comment TEXT
);