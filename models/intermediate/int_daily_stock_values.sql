{{ config(
    materialized='view'
) }}

with base as (

    select
        symbol,
        date,
        open,
        close,

        avg(open) over (
            partition by symbol
            order by date
            rows between 49 preceding and current row
        ) as ma_50_open,

        avg(close) over (
            partition by symbol
            order by date
            rows between 49 preceding and current row
        ) as ma_50_close,

        avg(open) over (
            partition by symbol
            order by date
            rows between 199 preceding and current row
        ) as ma_200_open,

        avg(close) over (
            partition by symbol
            order by date
            rows between 199 preceding and current row
        ) as ma_200_close

    from {{ ref('stg_stock_prices') }}

),

momentum as (

    select
        *,
        (ma_50_open - ma_200_open) as ma_open_diff,
        (ma_50_close - ma_200_close) as ma_close_diff,

        (ma_50_open - ma_200_open)
            - lag(ma_50_open - ma_200_open)
              over (partition by symbol order by date)
            as ma_open_momentum,

        (ma_50_close - ma_200_close)
            - lag(ma_50_close - ma_200_close)
              over (partition by symbol order by date)
            as ma_close_momentum

    from base
)

select *
from momentum
order by symbol, date desc