
  create view "alphyra"."staging_intermediate"."int_ml_ready_table__dbt_tmp"
    
    
  as (
    

with stock_ma as (
    SELECT
        symbol,
        date,
        ma_50_open,
        ma_200_open,
        ma_open_diff,
        ma_50_close,
        ma_200_close,
        ma_close_diff
    
    FROM "alphyra"."staging_intermediate"."int_daily_stock_values"
),

stock_ohlcv as (
    SELECT 
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume
    FROM "alphyra"."staging_staging"."stg_stock_prices"
),

stock_momentum as (
    SELECT
        symbol,
        date,
        ma_open_momentum,
        ma_close_momentum
    
    FROM "alphyra"."staging_intermediate"."int_daily_stock_values"
)


select * from stock_momentum
  );