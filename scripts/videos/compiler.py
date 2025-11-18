import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import timedelta

load_dotenv()

from scripts.util_functions import (
    find_time_range
)

from scripts.videos.youtube_api_functions import (
    search_youtube_videos,
    get_video_details,
    download_youtube_vid_mp3
)

from scripts.videos.insert_video_db import (
    insert_video_into_db
)

from scripts.analyze_db.database_functions import (
    get_news_db
)

def download_store_videos(query, folder_path):
    stock_news_df = get_news_db(query)
    stock_news_df['day_only'] = pd.to_datetime(stock_news_df['published_at']).dt.date

    grouped_stock_df = (
        stock_news_df
        .groupby(['company_name', 'day_only'])
        .agg({
            'sector': 'first',
            'symbol': 'first',
            'headline': list,
        })
        .reset_index()
    )

    video_id_set = set()

    for _, row in grouped_stock_df.iterrows():
        symbol = row['symbol']
        day = row['day_only']

        youtube_search = f"{symbol} stock analysis"
        pub_after, pub_before = find_time_range(str(day))

        video_ids = search_youtube_videos(youtube_search, pub_after, pub_before, max_results=1)

        for id in video_ids:
            video_id_set.add(id)
            video_details_dict = get_video_details(id)

            if not video_details_dict:
                print(f"[WARNING] Failed to fetch video details for {id}")
                continue

            symbol_folder = os.path.join(folder_path, symbol)
            os.makedirs(symbol_folder, exist_ok=True)

            transcript_path = os.path.join(symbol_folder, f"{id}.txt")

            video_details_df = pd.DataFrame([{
                'symbol': symbol,
                'video_id': id,
                'title': video_details_dict['title'],
                'url': video_details_dict['url'],
                'transcript_path': transcript_path,
                'publish_date': video_details_dict['published_at']
            }])

            success, error = insert_video_into_db(video_details_df)

            if success:
                print(f"[INFO] Successfully inserted {symbol} to raw.videos table")
            else:
                print(f"[WARNING] Failed to insert {symbol}: {error}")
            

    print("Function finished running!")


query = "SELECT * FROM raw.news WHERE symbol = 'NVDA' LIMIT 1"

download_store_videos(query, "downloads")