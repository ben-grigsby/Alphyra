
  create view "alphyra"."staging_intermediate"."int_market_snapshot__dbt_tmp"
    
    
  as (
    

select
    symbol,
    metric_name,
    metric_value,
    retrieved_at

from "alphyra"."staging_staging"."stg_company_financials"
where metric_category = 'market'
  );