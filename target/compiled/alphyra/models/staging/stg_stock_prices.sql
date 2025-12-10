

with stock_prices as (
    select 
        upper(trim(symbol)) as symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        created_at
    from "alphyra"."raw"."stock_prices"
),

renamed as (
    select
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        created_at
    from stock_prices
)

select *
from renamed