{{ config(
    materialized='view'
) }}

select
    upper(trim(symbol)) as symbol,
    trim(source) as source,
    upper(trim(metric_type)) as metric_type,
    trim(metric_name) as metric_name,
    trim(metric_period) as metric_period,
    metric_value,
    retrieved_at,
    raw_json,
    created_at
from {{ source('raw', 'company_financials')}}