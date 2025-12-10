
  create view "alphyra"."staging_staging"."stg_sentiment__dbt_tmp"
    
    
  as (
    

with sentiment as (
    select
        sentence,
        upper(trim(stock_symbol)) as symbol,
        positive_score,
        neutral_score,
        negative_score,
        model_name,
        source_type,
        source_url,
        published_at,
        created_at
    from "alphyra"."raw"."sentiment"
),

renamed as (
    select 
        sentence,
        symbol,
        positive_score,
        neutral_score,
        negative_score,
        model_name,
        source_type,
        source_url,
        published_at,
        created_at
    from sentiment
)

select *
from renamed
  );