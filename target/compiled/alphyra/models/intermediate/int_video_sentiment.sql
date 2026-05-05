

select
    content_id,
    AVG(positive_score) as positive_score,
    AVG(neutral_score) as neutral_score,
    AVG(negative_score) as negative_score
from "alphyra"."staging_staging"."stg_sentiment"
where source_type = 'VIDEO'
group by content_id