import os
import requests
import yt_dlp
import whisper
import isodate

from dotenv import load_dotenv

duration = "PT15M23S"

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

from scripts.videos.youtube_functions import (
    get_video_details,
    convert_duration,
    search_youtube_videos,
    download_audio
)

# for title, url, duration in search_youtube_videos("NVIDIA stock analysis"):
#     seconds = isodate.parse_duration(duration).total_seconds()
#     minutes = round(seconds / 60, 2)
#     print(f"{title} ({minutes} mins) - {url}")



if __name__ == '__main__':
    print("Starting video search...")
    video_ids = search_youtube_videos("NVIDIA stock analysis")
    video_info = get_video_details(video_ids)

    for title, url, duration in video_info:
        minutes, seconds = convert_duration(duration)
        print(f"{title}, {url}, {minutes} minutes {seconds} seconds.")

    test_download_vid = video_info[0][1]

    download_audio(test_download_vid, "nvidia_test")