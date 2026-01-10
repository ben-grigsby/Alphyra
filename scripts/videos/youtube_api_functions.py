import os
import requests
import yt_dlp

from dotenv import load_dotenv

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
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'publishedAfter': pub_after,
        'publishedBefore': pub_before,
        'key': API_KEY
    }

    response = requests.get(url, params=params)

    print(f"[YOUTUBE API] Status: {response.status_code}")
    if response.status_code != 200:
        print(f"[YOUTUBE API] Error response: {response.text}")

    data = response.json()

    # print(f"[DEBUG] API status: {response.status_code}")
    # print(f"[DEBUG] API response: {response.text}")

    video_ids = [item['id']['videoId'] for item in data.get('items', [])]
    return video_ids



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
        return None
    
    return {
        'title': item['snippet']['title'],
        'url': f"https://www.youtube.com/watch?v={video_id}",
        "duration": item["contentDetails"]["duration"],
        "published_at": item["snippet"]["publishedAt"],
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0)),
        "language": item["snippet"].get("defaultAudioLanguage", "unknown")
    }



def download_youtube_vid_mp3(url, full_output_path):
    """
    Download the audio track of a YouTube video and save it as an MP3 file.

    Args:
        url (str): The URL of the YouTube video.
        full_output_path (str): Full path for where the mp3 will be stored (ends in .mp3)
    Returns:
        None
    """

    print(f"Downloading video from {url}...")
    parent_dir = os.path.dirname(full_output_path)
    os.makedirs(parent_dir, exist_ok=True)

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

    print(f"Successfully downloaded video to {full_output_path}")

    return full_output_path


if __name__ == '__main__':
    pub_after  = "2025-12-08T00:00:00Z"
    pub_before = "2025-12-12T23:59:59Z"
    print(search_youtube_videos("NVDA stock analysis", pub_after, pub_before))