{{ config(
    materialized='view'
) }}

select
    upper(trim(symbol)) as symbol,
    trim(source) as source,
    upper(trim(metric_type)) as metric_type,
    upper(replace(trim(metric_name), ' ', '')) as metric_name,
    trim(metric_period) as metric_period,
    metric_value,

    case
        when metric_name ILIKE '%price%' then 'market'
        when metric_name ILIKE '%return%' then 'market'
        when metric_name ILIKE '%relative%' then 'market'
        when metric_name ILIKE '%ytd%' then 'market'
        when metric_name ILIKE '%month%' then 'market'
        when metric_name ILIKE '%week%' then 'market'
        when metric_name ILIKE '%day%' then 'market'
        when metric_name ILIKE 'pe%' then 'market'
        when metric_name ILIKE 'pb%' then 'market'
        when metric_name ILIKE 'ps%' then 'market'
        when metric_name ILIKE 'ptbv%' then 'market'
        when metric_name ILIKE 'pcf%' then 'market'
        when metric_name ILIKE 'pfcf%' then 'market'
        when metric_name ILIKE 'peg%' then 'market'
        when metric_name ILIKE '%marketcap%' then 'market'
        when metric_name ILIKE '%enterprisevalue%' then 'market'
        when metric_name ILIKE 'ev%' then 'market'
        when metric_name ILIKE '%beta%' then 'market'
        when metric_name ILIKE '%volume%' then 'market'
        when metric_name ILIKE '%trading%' then 'market'
        when metric_name ILIKE '%52week%' then 'market'
        when metric_name ILIKE '%13week%' then 'market'
        when metric_name ILIKE '%26week%' then 'market'
        when metric_name ILIKE '%10Day%' then 'market'
        when metric_name ILIKE '%3Month%' then 'market'

        when metric_name ILIKE '%margin%' then 'fundamentals'
        when metric_name ILIKE '%profit%' then 'fundamentals'  
        when metric_name ILIKE '%growth%' then 'fundamentals'
        when metric_name ILIKE '%cagr%' then 'fundamentals'
        when metric_name ILIKE '%ratio%' then 'fundamentals'
        when metric_name ILIKE '%coverage%' then 'fundamentals'
        when metric_name ILIKE '%revenue%' then 'fundamentals'
        when metric_name ILIKE '%income%' then 'fundamentals'
        when metric_name ILIKE '%eps%' then 'fundamentals'
        when metric_name ILIKE '%debt%' then 'fundamentals'
        when metric_name ILIKE '%equity%' then 'fundamentals'
        when metric_name ILIKE '%capital%' then 'fundamentals'
        when metric_name ILIKE '%asset%' then 'fundamentals'
        when metric_name ILIKE '%cash%' then 'fundamentals'
        when metric_name ILIKE '%fcf%' then 'fundamentals'
        when metric_name ILIKE '%focf%' then 'fundamentals'
        when metric_name ILIKE '%capex%' then 'fundamentals'
        when metric_name ILIKE '%turnover%' then 'fundamentals'
        when metric_name ILIKE '%perShare%' then 'fundamentals'
        when metric_name ILIKE '%employee%' then 'fundamentals'
        when metric_name ILIKE '%roe%' then 'fundamentals'
        when metric_name ILIKE '%roa%' then 'fundamentals'
        when metric_name ILIKE '%roi%' then 'fundamentals'
        when metric_name ILIKE '%roic%' then 'fundamentals'
        when metric_name ILIKE '%rotc%' then 'fundamentals'
        when metric_name ILIKE '%dividend%' then 'fundamentals'
        when metric_name ILIKE '%payout%' then 'fundamentals'
        when metric_name ILIKE '%bookValue%' then 'fundamentals'
        when metric_name ILIKE '%tangibleBookValue%' then 'fundamentals'
        when metric_name ILIKE '%tbv%' then 'fundamentals'
        when metric_name ILIKE '%shareOutstanding%' then 'fundamentals'
        when metric_name ILIKE '%currentRatio%' then 'fundamentals'
        when metric_name ILIKE '%quickRatio%' then 'fundamentals'
        when metric_name ILIKE '%cashRatio%' then 'fundamentals'
    else 'fundamentals'
    end as metric_category,

    retrieved_at,
    raw_json,
    created_at
from {{ source('raw', 'company_financials')}} 