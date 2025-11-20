import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import timedelta

load_dotenv()

from scripts.util_functions import (
    find_time_range,
    get_week_range
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
    stock_news_df['week_range'] = stock_news_df['day_only'].apply(get_week_range)
    
    grouped_stock_df = (
        stock_news_df
        .groupby(['symbol', 'week_range'])
        .agg({
            'sector': 'first',
            'company_name': 'first',
            'headline': list,
        })
        .reset_index()
    )

    print(grouped_stock_df.head())

    video_id_set = set()

    for _, row in grouped_stock_df.iterrows():
        if len(row['headline']) > 3:
            symbol = row['symbol']

            try:
                monday, friday = row['week_range']
            except Exception as e:
                print(f"[ERROR] Invalid week_range for {symbol}: {e}")
                continue

            youtube_search = f"{symbol} stock analysis"
            pub_after = str(monday)
            pub_before = str(friday + timedelta(days=1))

            video_ids = search_youtube_videos(youtube_search, pub_after, pub_before, max_results=50)

            if not video_ids:
                print(f"[INFO] No videos found for {symbol} between {pub_after} and {pub_before}")
                continue

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
                
        else:
            print(f"[SKIPPED] {symbol} had {len(row['headline'])} headlines — too few to run YouTube search.")

    print("Function finished running!")


query = "SELECT * FROM raw.news"

download_store_videos(query, "downloads")