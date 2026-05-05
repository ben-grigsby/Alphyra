
  create view "alphyra"."staging_intermediate"."int_news_sentiment__dbt_tmp"
    
    
  as (
    

select
    content_id,
    AVG(positive_score) as positive_score,
    AVG(neutral_score) as neutral_score,
    AVG(negative_score) as negative_score
from "alphyra"."staging_staging"."stg_sentiment"
where source_type != 'Video'
group by content_id
  );