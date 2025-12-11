{{ config(
    materialized='view'
) }}

with stock_ma as (
    SELECT
        symbol,
        date,
        ma_50_open,
        ma_200_open,
        ma_50_close,
        ma_200_close,
    
    FROM {{ref('int_daily_stock_values')}}
),

stock_ohlcv as (

)


select * from stock_values