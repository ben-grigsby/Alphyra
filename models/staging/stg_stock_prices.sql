{{ config(
    materialized='view'
)   }}

select
    id,
    upper(trim(symbol)) as symbol,
    date,
    open,
    high,
    low,
    close,
    volume,
    created_at
from {{ source('raw', 'stock_prices')}}