

with stock_values as (
    SELECT
        symbol,
        date,
        open,
        ma_50_open,
        ma_200_open,
        close,
        ma_50_close,
        ma_200_close,
        ma_open_diff,
        ma_close_diff,
        ma_open_momentum,
        ma_close_momentum
    
    FROM "alphyra"."staging_intermediate"."int_daily_stock_values"
)


select * from stock_values