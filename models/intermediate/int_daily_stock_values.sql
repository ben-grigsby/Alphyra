{{ config(
    materialized='view'
) }}

with stock_values as (
    SELECT
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        row_number() over (partition by symbol order by date desc) as rn
    FROM {{ref('stg_stock_prices')}}

),

daily_moving_average_50day as (
    SELECT
        symbol,
        round(avg(open)::numeric, 2) as open_ma_50day,
        round(avg(high)::numeric, 2) as high_ma_50day,
        round(avg(low)::numeric, 2) as low_ma_50day,
        round(avg(close)::numeric, 2) as close_ma_50day,
        round(avg(volume)::numeric, 2) as volume_ma_50day
    FROM stock_values
    WHERE rn <= 50
    GROUP BY symbol
),

daily_moving_average_200day AS (
    SELECT
        symbol,
        date,
        close,
        volume,

        round(
            avg(close) OVER (
                PARTITION BY symbol
                ORDER BY date
                ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
            )::numeric,
        2) AS close_ma_200,

        round(
            avg(volume) OVER (
                PARTITION BY symbol
                ORDER BY date
                ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
            )::numeric,
        2) AS volume_ma_200

    FROM stock_values
)

SELECT * FROM daily_moving_average_200day