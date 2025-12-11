

with stock_values as (
    SELECT
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        row_number() over (partition by symbol order by date asc) as rn
    FROM "alphyra"."staging_staging"."stg_stock_prices"

),

daily_50day_ma as (
    SELECT 
        symbol,
        date,

        open,
        AVG(open) OVER (
            PARTITION BY symbol
            ORDER BY date
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS ma_50_open,

        close,
        AVG(close) OVER (
            PARTITION BY symbol
            ORDER BY date
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) AS ma_50_close

    FROM stock_values
),

daily_200day_ma as (
    SELECT 
        symbol,
        date,

        open,
        AVG(open) OVER (
            PARTITION BY symbol
            ORDER BY date
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS ma_200_open,

        close,
        AVG(close) OVER (
            PARTITION BY symbol
            ORDER BY date 
            ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
        ) AS ma_200_close

    FROM stock_values
),

joined_table as (
    SELECT 

        f0.symbol,
        f0.date,
        f0.open,
        ma_50_open,
        ma_200_open,
        f0.close,
        ma_50_close,
        ma_200_close

    FROM daily_50day_ma f0
    JOIN daily_200day_ma t0
        ON f0.symbol = t0.symbol
        AND f0.date = t0.date
),

momentum as (
    SELECT 
        symbol,
        date,
        open,
        ma_50_open,
        ma_200_open,
        close,
        ma_50_close,
        ma_200_close,


        -- 1. DAILY DIFFERENCE
        (ma_50_open - ma_200_open) AS ma_open_diff,
        (ma_50_close - ma_200_close) AS ma_close_diff,

        -- 2. MOMENTUM
        (ma_50_open - ma_200_open) - lag(ma_50_open - ma_200_open) OVER (PARTITION BY symbol ORDER BY date) as ma_open_momentum,
        (ma_50_close - ma_200_close) - lag(ma_50_close - ma_200_close) OVER (PARTITION BY symbol ORDER BY date) as ma_close_momentum
    
    FROM joined_table
)

select * from momentum ORDER BY symbol, date desc