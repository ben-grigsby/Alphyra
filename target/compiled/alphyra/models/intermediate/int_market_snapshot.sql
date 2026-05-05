

select
    symbol,
    metric_name,
    metric_value,
    retrieved_at

from "alphyra"."staging_staging"."stg_company_financials"
where metric_category = 'market'