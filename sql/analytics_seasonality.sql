-- Аналитика 1: Динамика выставления накладных (MoM Growth)
WITH MonthlyStats AS (
    -- CTE (Обобщенное табличное выражение): сначала группируем данные по месяцам
    SELECT 
        DATE_TRUNC('month', invoice_date) AS month_start,
        COUNT(invoice_id) AS invoices_count
    FROM invoices
    WHERE invoice_date IS NOT NULL
    GROUP BY DATE_TRUNC('month', invoice_date)
)
SELECT 
    month_start,
    invoices_count,
    -- LAG "берет" значение из предыдущей строки (прошлый месяц)
    LAG(invoices_count) OVER (ORDER BY month_start) AS prev_month_count,
    -- Считаем процент роста. NULLIF спасает от ошибки деления на ноль
    ROUND(
        (invoices_count - LAG(invoices_count) OVER (ORDER BY month_start)) * 100.0 / 
        NULLIF(LAG(invoices_count) OVER (ORDER BY month_start), 0), 
    2) AS mom_growth_percent
FROM MonthlyStats
ORDER BY month_start;