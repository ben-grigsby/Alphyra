{{ config(
    materialized='view'
)}}

select
    symbol,
    metric_name,
    metric_value,
    retrieved_at

from {{ref('stg_company_financials')}}
where metric_category = 'market'