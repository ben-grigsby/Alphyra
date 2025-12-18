-- SELECT COUNT(DISTINCT source_url) FROM raw.sentiment
-- SELECT DISTINCT stock_symbol FROM raw.sentiment
-- TRUNCATE TABLE raw.stock_prices
-- SELECT DISTINCT metric_name FROM staging_staging.stg_company_financials LIMIT 10;

-- SELECT *
-- FROM staging_staging.stg_company_financials
-- WHERE metric_name ILIKE '%totalDebt%'
-- LIMIT 10;

-- SELECT *  
-- FROM staging_intermediate.int_company_features
-- WHERE symbol = 'NVDA'
-- LIMIT 10

-- SELECT * FROM staging_intermediate.int_daily_stock_values


SELECT * FROM raw.videos WHERE symbol = 'REMX'