{{ config(
    materialized='view'
) }}

with company_info as (
    SELECT 
        upper(trim(symbol)) as symbol,
        source,
        metric_type,
        metric_name,
        metric_period,
        metric_value,
        retrieved_at,
        raw_json,
        created_at
    
    FROM  {{source('raw', 'company_financials')}}
 ),

renamed as (
    SELECT 
        symbol,
        source,
        metric_type,
        metric_name,
        metric_period,
        metric_value::float as metric_value,
        retrieved_at::timestamp as retrieved_at,
        raw_json,
        created_at
    
    FROM company_info
)

SELECT *
FROM renamed