-- SELECT COUNT(DISTINCT source_url) FROM raw.sentiment
-- SELECT DISTINCT stock_symbol FROM raw.sentiment
-- TRUNCATE TABLE raw.sentiment
SELECT * FROM staging_staging.stg_company_financials LIMIT 10;
