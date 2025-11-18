from scripts.videos.youtube_functions import (
    get_video_details,
    search_youtube_videos
)

video_info = get_video_details(search_youtube_videos(("stock analysis")))

for info in video_info:
    print(info[0])
    print(info[1])
    print("\n")
