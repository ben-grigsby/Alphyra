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


def search_stock_video_ids(query, folder_path, from_date, to_date, max_runs=5):
    stock_news_df = get_db_info(query)

    stock_news_df = stock_news_df[
        (stock_news_df['published_at'] >= from_date) &
        (stock_news_df['published_at'] <= to_date)
    ]

    stock_news_df['day_only'] = pd.to_datetime(stock_news_df['published_at']).dt.date
    stock_news_df['week_range'] = stock_news_df['day_only'].apply(get_week_range)
    
    grouped_stock_df = (
        stock_news_df
        .groupby(['symbol', 'week_range'])
        .agg({
            'sector': 'first',
            'company_name': 'first',
            'headline': list,
            'created_at': 'max'
        })
        .reset_index()
    )

    grouped_stock_df = grouped_stock_df.sort_values("created_at", ascending=True)

    video_id_set = set()
    run_count = 0

    for _, row in grouped_stock_df.iterrows():

        # if run_count >= max_runs:
        #     print(f"[INFO] Reached testing limit of {max_runs} stocks. Stopping early.")
        #     break

        symbol = row['symbol']

        if len(row['headline']) > 3:
            print("\n")
            print(f"[INFO] RUN {run_count} ")
            print("\n")

            try:
                monday, friday = row['week_range']
            except Exception as e:
                print(f"[ERROR] Invalid week_range for {symbol}: {e}")
                continue

            youtube_search = f"{symbol} stock analysis"
            pub_after = f"{monday}T00:00:00Z"   # Start of Monday
            pub_before = f"{friday + timedelta(days=1)}T00:00:00Z"  # Start of Saturday

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
            
            run_count += 1
        else:
            print(f"[SKIPPED] {symbol} had {len(row['headline'])} headlines — too few to run YouTube search.")

    print("Function finished running!")



def process_single_video(row, news_df, output_dir):
    try:
        symbol = row['symbol']
        filename = row['video_id']
        url = row['url']
        id = row['video_id']
        publish_date = row['publish_date']

        output_path = f"downloads/{symbol}"

        print(f"[INFO] Currently downloading {symbol}: {id} -> {output_path}")

        mp3_full_output_path = f"{download_youtube_vid_mp3(url, filename, output_path)}.mp3"

        print(f"[INFO] Completed downloading {symbol}: {id} -> {output_path}")
        print("\n")

        transcript_path = transcribe_mp3(mp3_full_output_path, output_dir)

        if os.path.exists(mp3_full_output_path):
            # print(f"[TEST] Deleting {mp3_full_output_path}")
            os.remove(mp3_full_output_path)
            print(f"[INFO] Deleted: {mp3_full_output_path}")
        else:
            print("[ERROR] File does not exist")

        sentiment_records = []
        
        sentences = split_into_sentences(transcript_path)

        for sent in sentences:
            sentiment_analysis = analyze_sentiment(sent)
            print(f"[DEBUG] Sentiment result: {sentiment_analysis}")
            sentiment_records.append({
                'sentence': sent,
                'stock_symbol': symbol,
                'positive_score': sentiment_analysis['positive'],
                'neutral_score': sentiment_analysis['neutral'],
                'negative_score': sentiment_analysis['negative'],
                'model_name': "FinBERT",
                'source_type': 'Youtube',
                'source_url': url,
                'published_at': publish_date
            })

        sentiment_df = pd.DataFrame(sentiment_records)
        
        insert_stat, error = insert_sentiment_into_db(sentiment_df)

        if insert_stat:
            save_processed_id(id)
            return f"[INFO] Successfully inserted {symbol} video {id} into database"
        
    except Exception as e:
        return f"[ERROR] Unable to insert video {id} into database. Error: {e}"



def download_transcribe_analyze_mp3(query_news, query_videos, output_dir, max_threads=4):

    video_id_df = get_db_info(query_videos)
    news_df = get_db_info(query_news)

    futures = []
    processed_ids = load_processed_ids()
    max_videos = 4
    count = 0 

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for _, row in video_id_df.iterrows():
            if count > max_videos:
                break
            if row['video_id'] in processed_ids:
                continue
            futures.append(executor.submit(process_single_video, row, news_df, output_dir))
            count += 1
        
        for future in as_completed(futures):
            print(future.result())
    


if __name__ == '__main__':
    query1 = "SELECT * FROM raw.news"
    query2 = "SELECT * FROM raw.videos"

    download_transcribe_analyze_mp3(query1,  query2, "downloads/transcriptions")

