

with news_sentiment as (
    SELECT
        symbol,
        positive_score,
        neutral_score,
        negative_score,
        published_at::date as published_date
    FROM "alphyra"."staging_staging"."stg_sentiment"
    WHERE source_type != 'Youtube'
),

daily_company_sentiment as (
    SELECT
        symbol,
        published_date,
        AVG(positive_score) AS positive_score,
        AVG(neutral_score) AS neutral_score,
        AVG(negative_score) AS negative_score
    FROM news_sentiment
    GROUP BY symbol, published_date
)

select * from daily_company_sentiment