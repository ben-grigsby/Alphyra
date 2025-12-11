

with video_sentiment as (
    SELECT
        symbol,
        positive_score,
        neutral_score,
        negative_score,
        source_url,
        published_at::date as published_date
    FROM "alphyra"."staging_staging"."stg_sentiment"
    WHERE source_type = 'Youtube'
),

stock_video_sentiment as (
    SELECT 
        symbol,
        published_date,
        AVG(positive_score) AS positive_score,
        AVG(neutral_score) AS neutral_score,
        AVG(negative_score) AS negative_score
    FROM video_sentiment
    GROUP BY symbol, published_date
)

select * from stock_video_sentiment