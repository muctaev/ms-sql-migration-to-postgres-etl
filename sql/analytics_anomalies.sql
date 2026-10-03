-- Аналитика 3: Поиск аномальной активности по дням
SELECT 
    invoice_date,
    invoice_number,
    comment,
    -- Считаем количество накладных в рамках каждой даты (PARTITION BY)
    COUNT(invoice_id) OVER(PARTITION BY invoice_date) AS daily_invoices_count
FROM invoices
WHERE invoice_date IS NOT NULL
ORDER BY daily_invoices_count DESC, invoice_date;