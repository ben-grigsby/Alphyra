

select
    id,
    content_id,
    upper(trim(symbol)) as symbol,
    trim(video_id) as video_id,
    trim(title) as title,
    trim(url) as url,
    trim(transcript_path) as transcript_path,
    is_copy,
    cast(publish_date as timestamp) as publish_date,
    created_at
from "alphyra"."raw"."videos"
where content_id is not null