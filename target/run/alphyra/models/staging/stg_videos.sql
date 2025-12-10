
  create view "alphyra"."staging_staging"."stg_videos__dbt_tmp"
    
    
  as (
    

with videos as (
    select
        upper(trim(symbol)) as symbol,
        video_id,
        title,
        url,
        transcript_path,
        publish_date,
        created_at
    from "alphyra"."raw"."videos"
),

renamed as (
    select
        symbol,
        video_id,
        title,
        url,
        transcript_path,
        publish_date,
        created_at
    from videos
)

select *
from renamed
  );