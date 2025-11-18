import os 
import requests
import yt_dlp
import whisper
import isodate

from dotenv import load_dotenv

duration = "PT15M235"
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")



def search_youtube_videos(query, pub_after, pub_before, max_results=5):
    """
    Search YouTube for videos matching a query within a specified date range.

    Parameters
    ----------
    query : str
        The search term to query (e.g., "AAPL stock analysis").
    pub_after : str
        ISO 8601 formatted start date for filtering results 
        (e.g., "2025-11-01T00:00:00Z").
    pub_before : str
        ISO 8601 formatted end date for filtering results 
        (e.g., "2025-11-02T00:00:00Z").
    max_results : int, optional
        Maximum number of video results to return (default is 5).

    Returns
    -------
    list of str
        A list of YouTube video IDs that match the search criteria.
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 5,
        "publishedAfter": pub_after,
        "publishedBefore": pub_before,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
    return video_ids



def convert_duration(duration):
    """
    Convert an ISO 8601 duration string to minutes and seconds.

    Args:
        duration (str): Duration string in ISO 8601 format (e.g., 'PT15M23S').

    Returns:
        tuple: A tuple containing two integers — (minutes, seconds).
    """
    parsed = isodate.parse_duration(duration)

    total_seconds = int(parsed.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return minutes, seconds



def get_video_details(video_id):
    """
    Retrieve video metadata for a single YouTube video ID.

    Args:
        video_id (str): A YouTube video ID.

    Returns:
        dict: Contains title, url, duration, publish date, view count,
              like count, comment count, and original language (if available).
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    item = data.get("items", [None])[0]
    if item is None:
        return None  # or raise an exception / return {}

    return {
        "title": item["snippet"]["title"],
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "duration": item["contentDetails"]["duration"],
        "published_at": item["snippet"]["publishedAt"],
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0)),
        "language": item["snippet"].get("defaultAudioLanguage", "unknown")
    }



def download_audio(url, filename, output_path="downloads"):
    """
    Download the audio track of a YouTube video and save it as an MP3 file.

    Args:
        url (str): The URL of the YouTube video.
        filename (str): The name of the output MP3 file (should include .mp3).
        output_path (str): Directory where the file will be saved (default is 'downloads').

    Returns:
        None
    """

    print(f"Downloading video from {url}...")
    os.makedirs(output_path, exist_ok=True)
    full_output_path = os.path.join(output_path, filename)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': full_output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"Successfully downloaded {filename}")



video_ids = search_youtube_videos("NVDA stock analysis", '2025-11-13T00:00:00Z', '2025-11-14T23:59:59Z')

for id in video_ids:
    print(get_video_details(id))
    print("\n")
