{{ config(
    materialized='view'
) }}

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
    
    FROM {{ref('int_daily_stock_values')}}
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
    FROM {{ref('stg_stock_prices')}}
),

stock_momentum as (
    SELECT
        symbol,
        date,
        ma_open_momentum,
        ma_close_momentum
    
    FROM {{ref('int_daily_stock_values')}}
),

