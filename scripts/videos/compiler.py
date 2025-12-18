import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

from scripts.util_functions import (
    find_time_range,
    get_week_range,
    save_processed_id,
    load_processed_ids
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
    get_db_info,
    insert_sentiment_into_db
)

from scripts.videos.mp3_functions import (
    transcribe_mp3
)

from scripts.transcriptions.text_chunking_functions import (
    split_into_sentences
)

from scripts.sentiment.finbert_sentiment import (
    analyze_sentiment
)



def check_existing_video_id(new_video_zip, existing_video_zip_lst_set):
    # zip = (symbol, video_id)
    if new_video_zip in existing_video_zip_lst_set:
        print(f"[INFO] Duplicate video for {new_video_zip[0]} encountered.")
        return False
    
    else:
        return True



def edit_raw_videos(news_db_query, video_df_query, pub_after, pub_before):
    print("Starting video search and download function...")

    pub_after = f"{pub_after}T00:00:00Z"
    pub_before = f"{pub_before}T23:59:59Z"

    existing_stocks = set(get_db_info(news_db_query)['symbol'].unique().tolist())
    all_existing_videos_info_df = get_db_info(video_df_query)
    existing_stock_video_tuple = set(
        tuple(x)
        for x in all_existing_videos_info_df[['symbol', 'video_id']].copy().itertuples(index=False)
    )
    existing_video_ids = {t[1] for t in existing_stock_video_tuple}

    df_lst = []

    for stock in existing_stocks:

        search_query = f"{stock} stock analysis"
        stock_video_ids_lst = search_youtube_videos(search_query, pub_after, pub_before)

        if not stock_video_ids_lst:
            print(f"No videos for {stock} from {pub_after} to {pub_before}, moving on...")
            continue

        symbol_id_zip = {(stock, id) for id in stock_video_ids_lst}
        new_video_ids = symbol_id_zip - existing_stock_video_tuple

        video_to_copy = {t[1] for t in new_video_ids if t[1] in existing_video_ids}
        video_to_download = {t[1] for t in new_video_ids if t[1] not in existing_video_ids}

        for id in video_to_copy:
            print(f"Copying video id to be assigned to {stock}...")

            transcript_path = f"downloads/{stock}/{id}"
            
            existing_video_df = all_existing_videos_info_df[all_existing_videos_info_df['video_id'] == id][['title', 'url', 'publish_date']].copy()
            existing_video_df['symbol'] = stock
            existing_video_df['transcript_path'] = transcript_path


            df_lst.append(existing_video_df)

        print(f"Already found IDs: {df_lst}")
        
        for id in video_to_download:
            print(f"Registering {id} video for {stock}")

            downloaded_video_info = get_video_details(id)

            if downloaded_video_info:
                print(f"Obtaining info for {stock} video {id}...")
                transcript_path = f"downloads/{stock}/{id}"

                video_info_df = {
                    'symbol': stock,
                    'video_id': id,
                    'title': downloaded_video_info['title'],
                    'url': downloaded_video_info['url'],
                    'transcript_path': transcript_path,
                    'publish_date': downloaded_video_info['published_at']
                }

                video_info_df = pd.DataFrame([video_info_df])

                df_lst.append(video_info_df)
                print(f"Appended video {id} info to list of DataFrames")
            
            else:
                continue
    
    if not df_lst:
        print(f"[INFO] No new videos to add")
        return False, "No new video records", None
    
    final_df = pd.concat(df_lst, ignore_index=True)

    if final_df.empty or final_df is None:
        return False, "Nothing to append to raw.videos"

    status, error = insert_video_into_db(final_df)
    
    return status, error, final_df



def download_and_process_videos(get_video_info_query, output_dir):
    video_df = get_db_info(get_video_info_query)
    url_and_path = video_df[['url', 'transcript_path']]


    for _, row in url_and_path.iterrows():
        stem = row['transcript_path']
        parent_dir = os.path.dirname(row['transcript_path'])
        mp3_transcript_path = f"{stem}/audio"
        video_url = row['url']
        
        os.makedirs(parent_dir, exist_ok=True)

        mp3_path = download_youtube_vid_mp3(video_url, mp3_transcript_path)
        transcription_path = transcribe_mp3(f"{mp3_path}.mp3", stem)

        print(transcription_path)
        
        if transcription_path and os.path.exists(transcription_path) and os.path.getsize(transcription_path) > 0:
            os.remove(f"{mp3_path}.mp3")
            print(f"[INFO] Successfully removed the {mp3_path}.mp3 file.")


        
if __name__ == '__main__':
    news_query = """
        SELECT * FROM raw.news WHERE symbol = 'REMX'
    """
    all_video_query = """
        SELECT * FROM raw.videos
    """
    video_url_path_query = """
        SELECT * FROM raw.videos WHERE symbol = 'REMX'
    """

    pub_after = "2025-12-08"
    pub_before = "2025-12-12"

    output_dir = "downloads/transcriptions"

    # lst_dfs = edit_raw_videos(news_query, all_video_query, pub_after, pub_before)
    # print(lst_dfs)

    download_and_process_videos(video_url_path_query, output_dir)

