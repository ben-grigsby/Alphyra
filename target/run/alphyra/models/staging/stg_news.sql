
  create view "alphyra"."staging_staging"."stg_news__dbt_tmp"
    
    
  as (
    

select 
    coalesce(trim(company_name), '') as company_name,
    upper(trim(sector)) as sector,
    upper(trim(symbol)) as symbol,
    coalesce(trim(headline), '') as headline,
    trim(summary) as summary,
    upper(trim(source)) as source,
    upper(trim(category)) as category,
    cast(published_at as timestamp) as published_at,
    trim(url) as url,
    raw_json,
    created_at
from "alphyra"."raw"."news"
where symbol is not null
  );