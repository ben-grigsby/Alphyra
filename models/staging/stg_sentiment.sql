{{ config(
    materialized='view'
) }}

select
    id,
    content_id,
    trim(sentence) as sentence,
    positive_score,
    neutral_score,
    negative_score,
    model_name,
    upper(trim(source_type)) as source_type,
    trim(source_url) as source_url,
    cast(published_at as timestamp) as published_at,
    created_at
from {{ source('raw', 'sentiment')}}