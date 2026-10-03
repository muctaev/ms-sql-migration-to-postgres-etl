-- Аналитика 2: Ценовое ранжирование ассортимента
SELECT 
    article,
    product_name,
    price,
    -- NTILE(3) делит все товары на 3 равные группы по возрастанию цены
    NTILE(3) OVER (ORDER BY price) AS segment_id,
    -- CASE превращает цифры 1, 2, 3 в понятные бизнес-названия
    CASE NTILE(3) OVER (ORDER BY price)
        WHEN 1 THEN 'Эконом'
        WHEN 2 THEN 'Стандарт'
        WHEN 3 THEN 'Премиум'
    END AS segment_name
FROM products
WHERE price IS NOT NULL
ORDER BY price;