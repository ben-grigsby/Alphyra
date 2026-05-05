
  create view "alphyra"."staging_staging"."stg_stock_prices__dbt_tmp"
    
    
  as (
    

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
  );