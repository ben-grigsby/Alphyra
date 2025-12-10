
  create view "alphyra"."staging_staging"."stg_news__dbt_tmp"
    
    
  as (
    

with news as (
    select
        trim(company_name) as company_name,
        trim(sector) as sector,
        upper(trim(symbol)) as symbol,
        headline,
        summary,
        source,
        category,
        published_at,
        url,
        raw_json,
        created_at
    from "alphyra"."raw"."news"
),

renamed as (
    select
        company_name,
        sector,
        symbol,
        headline,
        summary,
        source,
        category,
        published_at,
        url,
        raw_json,
        created_at
    from news
)

select *
from renamed
  );