

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
from "alphyra"."raw"."stock_prices"