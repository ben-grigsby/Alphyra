{{ config(
    materialized='view'
) }}

with company_metrics as (
    SELECT 
        symbol,
        source,
        metric_type,
        metric_name,
        metric_period,
        metric_value,
        retrieved_at,
        retrieved_date,
        raw_json,
        created_at
    
    FROM {{ref('stg_company_financials')}}
),

grouped_by_company as (
    SELECT
        symbol,
        retrieved_date,

        -- pivot points
        max(case when metric_name = 'psTTM' then metric_value end) as PS_TTM,
        max(case when metric_name = 'revenueGrowth5Y' then metric_value end) as REVENUE_GROWTH_5Y,
        max(case when metric_name = 'roiTTM' then metric_value end) as ROI_TTM,
        max(case when metric_name = 'quickRatioQuarterly' then metric_value end) as QUICK_RATIO_QUARTERLY,
        max(case when metric_name = 'netProfitMarginTTM' then metric_value end) as NET_PROFIT_MARGIN_TTM,
        max(case when metric_name = 'epsGrowthTTMYoy' then metric_value end) as EPS_GROWTH_TTM_YOY,
        max(case when metric_name = 'totalDebt/totalEquityQuarterly' then metric_value end) as TOTAL_DEBT_TOTAL_EQUITY

    FROM company_metrics
    GROUP BY symbol, retrieved_date
)

select *
from grouped_by_company