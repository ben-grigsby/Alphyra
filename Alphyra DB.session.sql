-- SELECT COUNT(DISTINCT source_url) FROM raw.sentiment
-- SELECT DISTINCT stock_symbol FROM raw.sentiment
-- TRUNCATE TABLE raw.news
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


-- SELECT * FROM raw.news WHERE url = 'https://finnhub.io/api/news?id=e3da97c6748721eec27e9329314b3e45dc983f59c02dba4b13ed671232ee86fe'

SELECT * FROM raw.videos