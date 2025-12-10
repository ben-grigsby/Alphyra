
  create view "alphyra"."staging_intermediate"."int_daily_stock_values__dbt_tmp"
    
    
  as (
    

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
    FROM "alphyra"."staging_staging"."stg_stock_prices"

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
        s.symbol,
        s.date,
        s.close,
        s.volume,

        ma50.close_ma_50,
        ma50.volume_ma_50,

        ma200.close_ma_200,
        ma200.volume_ma_200

    FROM stock_values s
    LEFT JOIN daily_moving_average_50day ma50
        ON s.symbol = ma50.symbol AND s.date = ma50.date
    LEFT JOIN daily_moving_average_200day ma200
        ON s.symbol = ma200.symbol AND s.date = ma200.date
    ORDER BY s.symbol, s.date
)

SELECT * FROM daily_moving_average_200day
  );