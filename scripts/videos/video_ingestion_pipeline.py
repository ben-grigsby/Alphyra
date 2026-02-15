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
    load_processed_ids,
    val_in_list_mask_df
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



# def check_existing_video_id(new_video_zip, existing_video_zip_lst_set):
#     # zip = (symbol, video_id)
#     if new_video_zip in existing_video_zip_lst_set:
#         print(f"[INFO] Duplicate video for {new_video_zip[0]} encountered.")
#         return False
    
#     else:
#         return True



def acquire_video_information(news_db_query, video_df_query, pub_after, pub_before, BATCH_SIZE=100):
    print("Starting video search and download function...")

    pub_after = f"{pub_after}T00:00:00Z"
    pub_before = f"{pub_before}T23:59:59Z"

    stocks_from_raw_news_df = get_db_info(news_db_query)
    processed_videos_df = get_db_info(video_df_query)

    if stocks_from_raw_news_df.empty:
        print(f"[ERROR] There are no stocks in raw.news to research videos of")
        return
    if processed_videos_df.empty:
        print(f"[INFO] First time downloading and analyzing videos")
    
    stocks_from_raw_news_set = set(stocks_from_raw_news_df['symbol'].unique().tolist())
    processed_videos_tuple_set = set(
        tuple(x)
        for x in processed_videos_df[['symbol', 'video_id']].copy().itertuples(index=False)
    )

    processed_videos_id_set = {t[1] for t in processed_videos_tuple_set}

    buffer = []

    for stock in stocks_from_raw_news_set:
        print(f"Beginning {stock} video search for time interval {pub_after} - {pub_before}...")

        search_query = f"{stock} stock analysis"

        stock_video_ids_set = set(search_youtube_videos(search_query, pub_after, pub_before))

        if not stock_video_ids_set:
            print(f"[INFO] No videos found for {stock} from {pub_after} - {pub_before}")
            continue

        new_videos_set = stock_video_ids_set - processed_videos_id_set
        duplicate_videos_set = stock_video_ids_set & processed_videos_id_set


        if new_videos_set:
            for video_id in new_videos_set:
                print(f"[INFO] Registering new id: {video_id} for {stock}")

                downloaded_video_info = get_video_details(video_id)

                if downloaded_video_info:
                    print(f"Obtaining video info for {stock} video {video_id}...")

                    transcript_path = f"downloads/{video_id}"

                    video_info_dict = {
                        'symbol': stock,
                        'video_id': video_id,
                        'title': downloaded_video_info['title'],
                        'url': downloaded_video_info['url'],
                        'transcript_path': transcript_path,
                        'publish_date': downloaded_video_info['published_at'],
                        'is_copy': False
                    }


                    processed_videos_id_set.add(video_id)

                    processed_videos_df = pd.concat(
                        [processed_videos_df, pd.DataFrame([video_info_dict])],
                        ignore_index=True
                    )

                    buffer.append(video_info_dict)

                    print(f"[INFO] Appended {video_id} info for {stock} to df_lst")
                
                else:
                    print(f"[ERROR] An error occurred when attempting to download {video_id} for {stock}")
                    continue
        else:
            print(f"[INFO] No new videos for {stock}")

        
        if duplicate_videos_set:
            for video_id in duplicate_videos_set:
                print(f"[INFO] Copying {video_id} to {stock}")

                transcript_path = f"downloads/{video_id}"

                video_info = processed_videos_df[processed_videos_df['video_id'] == video_id].iloc[[0]].copy()
                video_row = video_info.iloc[0]

                if not video_info.empty:
                    repeated_video_df = {
                        "symbol": stock,
                        "video_id": video_row['video_id'],
                        "title": video_row['title'],
                        "url": video_row['url'],
                        "transcript_path": transcript_path,
                        "publish_date": video_row['publish_date'],
                        "is_copy": True
                    }

                    buffer.append(repeated_video_df)

                    print(f"[INFO] Appended {video_row['video_id']} info for {stock} to df_lst")
        
        if len(buffer) >= 100:
            buffer_df = pd.DataFrame(buffer)
            print(f"[INFO] Buffer dataframe has exceeded batch limit of {BATCH_SIZE}...appending buffer to SQL table")
            status, message = insert_video_into_db(buffer_df)

            if status:
                print(f"[INFO] Buffer dataframe has been appended to raw.videos")
                print(f"[INFO] Preparing to cleanup buffer dataframe")

                buffer = []
            else:
                print(f"[ERROR] An error occurred when appending the buffer dataframe to raw.videos...")
                print(f"[ERROR]    {message}")

        # else:
        #     print(f"[INFO] No repeated videos for {stock}")
    
    if buffer:
        buffer_df = pd.DataFrame(buffer)
        print("[INFO] Flushing remaining buffer to raw.videos")
        status, message = insert_video_into_db(buffer_df)

        if status:
            print(f"[INFO] Successfully appended remaining buffer videos to raw.videos")

        else:
            print(f"[ERROR] An error occurred when appending the remaining buffer videos to raw.videos...")
            print(f"[ERROR]    {message}")



def download_transcribe_video(row):
    """
    Downloads audio for a single video and generates its transcript.

    Parameters
    ----------
    row : pandas.Series
        Row from raw.videos DataFrame containing:
            - transcript_path
            - url

    Returns
    -------
    str or None
        Path to generated transcript file if successful.
        None if download or transcription fails.

    Side Effects
    ------------
    - Creates transcript directory if it does not exist.
    - Downloads YouTube audio (.mp3).
    - Runs transcription process.
    - Deletes audio file after successful transcription.
    """
    
    stem = row['transcript_path']
    mp3_transcription_path = os.path.join(stem, "audio")
    video_url = row['url']

    os.makedirs(stem, exist_ok=True)

    mp3_path = download_youtube_vid_mp3(video_url, mp3_transcription_path)
    transcription_path = transcribe_mp3(f"{mp3_path}.mp3", stem)

    if transcription_path and os.path.exists(transcription_path) and os.path.getsize(transcription_path) > 0:
        os.remove(f"{mp3_path}.mp3")
        print(f"[INFO] Successfully removed the {mp3_path}.mp3 file")
        return transcription_path
    else:
        print(f"[ERROR] Unable to delete file at {mp3_path}")
        return None



def analyze_video_sentiment(video_text_path):
    print("[INFO] Splitting video transcription into sentences")

    video_sentences = split_into_sentences(video_text_path)

    # print(video_sentences[0])

    print("[INFO] Analyzing sentence sentiment")
    video_per_sentence_sentiment = analyze_sentiment(text=video_sentences)

    # print(video_per_sentence_sentiment)

    sentence_sentiment_dict = {
        "Sentence": [],
        "Neutral": [],
        "Positive": [],
        "Negative": []
    }

    return video_per_sentence_sentiment, video_sentences



def combine_sentence_sentiment(video_text_path):
    print("[INFO] Initiating video sentiment analysis process")

    sentence_sentiment, sentences = analyze_video_sentiment(video_text_path)

    assert len(sentences) == len(sentence_sentiment), \
        "Sentence / sentiment length mismatch"

    sentence_sentiment_dict = {
        "sentence": [],
        "neutral_score": [],
        "positive_score": [],
        "negative_score": []
    }

    for i in range(len(sentences)):
        sentence_sentiment_dict['sentence'].append(sentences[i])
        sentence_sentiment_dict['neutral_score'].append(sentence_sentiment[i]["neutral"])
        sentence_sentiment_dict['positive_score'].append(sentence_sentiment[i]["positive"])
        sentence_sentiment_dict['negative_score'].append(sentence_sentiment[i]["negative"])
    
    df = pd.DataFrame(sentence_sentiment_dict)

    return df



def download_and_process_videos(get_video_info_query, analyzed_videos_query, buffer_max):
    """
    End-to-end video ingestion and sentiment processing pipeline.

    This function:
        1. Retrieves raw video metadata from the database.
        2. Identifies videos that have not yet been sentiment-analyzed
           (based on source_url presence in raw.sentiment).
        3. Downloads and transcribes each new video.
        4. Performs sentence-level sentiment analysis using FinnBert.
        5. Buffers results and batch-inserts them into the raw.sentiment table.

    Parameters
    ----------
    get_video_info_query : str
        SQL query that returns video metadata from raw.videos.
        Must include columns:
            - url
            - transcript_path
            - publish_date
            - is_copy

    analyzed_videos_query : str
        SQL query that returns existing analyzed source URLs from raw.sentiment.
        Must include column:
            - source_url

    buffer_max : int
        Maximum number of video sentiment DataFrames to accumulate
        before batch inserting into the database.

    Behavior
    --------
    - Ensures idempotency by skipping videos whose URLs already exist
      in raw.sentiment.
    - Uses batched inserts for performance.
    - Flushes any remaining buffered sentiment rows after loop completion.
    - Logs processing steps and errors.

    Notes
    -----
    - Deduplication is currently based only on source_url.
      Future model-versioning may require (source_url, model_name) dedup keys.
    - Buffer size is based on number of processed videos, not total sentiment rows.
    """

    raw_videos_df = get_db_info(get_video_info_query)
    analyzed_videos_df = get_db_info(analyzed_videos_query)

    video_urls_set = set(raw_videos_df['url'])
    analyzed_videos_url_set = set(analyzed_videos_df['source_url'])

    new_video_urls_set = video_urls_set - analyzed_videos_url_set

    new_videos_df = raw_videos_df[raw_videos_df['url'].isin(new_video_urls_set)]
    
    original_new_videos_df = new_videos_df[new_videos_df['is_copy'] == False]

    buffer = []

    for _, row in original_new_videos_df.iterrows():
        video_transcription_path = download_transcribe_video(row)
        if video_transcription_path:
            print(f"[INFO] Accessing {video_transcription_path}")
            video_sentiment_df = combine_sentence_sentiment(video_transcription_path)
            video_sentiment_df['model_name'] = 'FinnBert'
            video_sentiment_df['source_type'] = 'Video'
            video_sentiment_df['source_url'] = row['url']
            video_sentiment_df['published_at'] = row['publish_date']

            buffer.append(video_sentiment_df)

            print(f"[DEBUG] Buffer length: {len(buffer)}")

            if len(buffer) >= buffer_max:
                buffer_df = pd.concat(buffer, ignore_index=True)
                print(f"[INFO] Sentiment buffer dataframe has exceeded data limit of {buffer_max}...appending buffer to raw.sentiment table")
                status, message = insert_sentiment_into_db(buffer_df)

                if status:
                    print(f"[INFO] Sentiment buffer dataframe has been appended to raw.sentiment")
                    print(f"[INFO] Preparing to cleanup sentiment buffer dataframe")

                    buffer = []
                
                else:
                    print(f"[ERROR] An error occurred when appending the sentiment buffer dataframe to raw.sentiment...")
                    print(f"[ERROR]    {message}")
                
    if buffer:
        buffer_df = pd.concat(buffer, ignore_index=True)
        print(f"[INFO] Flushing remaining sentiment buffer to raw.sentiment")
        status,  message = insert_sentiment_into_db(buffer_df)

        if status:
            print(f"[INFO] Successfully appended remaining sentiment buffer videos to raw.sentiment")

        else:
            print(f"[ERROR] An error occurred when appending the remaining sentiment buffer videos to raw.sentiment...")
            print(f"[ERROR]    {message}")


def compiler(news_db_query, video_df_query, pub_after, pub_before, get_video_info_query):
    video_search_status, video_search_error, video_search_df = acquire_video_information(news_db_query, video_df_query, pub_after, pub_before)

    if video_search_status and video_search_error == None and not video_search_df.empty:
        print(f"[INFO] Successfully updated raw.videos dataframe to include new stock videos from {pub_after} to {pub_before}")
    elif video_search_status and video_search_error == None and video_search_df.empty:
        print(f"[INFO] No new rows added into raw.videos on account of empty DataFrame: {video_search_df.head()}")
    else:
        print(f"[ERROR] An error occurred when trying to update raw.videos. Status: {video_search_status}    Error: {video_search_error}")
        return False

    video_info = download_and_process_videos(get_video_info_query)

    return video_info

    #### [NEXT STEPS] I have completed the search, download, and sentiment analysis part of this file. The next step is to figure out how to 
    #### combine all the information from these three separate functions together into a row that I can insert into my raw.sentiment table



def temp_insert_sentiment(df):

    df['stock_symbol'] = 'REMX'
    df['model_name'] = 'FinBERT'
    df['source_type'] = 'Youtube'
    df['source_url'] = 'N/A'
    df['published_at'] = '2025-11-12 11:58:03'

    status, error = insert_sentiment_into_db(df)

    return df, status, error


        
if __name__ == '__main__':
    news_query = """
        SELECT * FROM raw.news 
    """
    all_video_query = """
        SELECT * FROM raw.videos
    """
    video_url_path_query = """
        SELECT * FROM raw.videos WHERE symbol = 'NVDA'
    """
    analyzed_videos_query = """
        SELECT * FROM raw.sentiment
    """

    pub_after = "2026-02-02"
    pub_before = "2026-02-06"

    output_dir = "downloads/transcriptions"

    # lst_dfs = edit_raw_videos(news_query, all_video_query, pub_after, pub_before)

    # print("ENTER __main__")

    # transcript_path = "downloads/NVDA/6jd5lUg3zXY/transcript.txt"
    
    # sentiment_df = combine_sentence_sentiment(transcript_path)

    # print(sentiment_df.head())
    acquire_video_information(news_query, all_video_query, pub_after, pub_before)
    video_df = download_and_process_videos(video_url_path_query, analyzed_videos_query, 5)

    print(video_df)

    # print("FINAL OUTPUT: ")
    # print(video_df.head())

    # tmp_df, status, error = temp_insert_sentiment(combine_sentence_sentiment(transcript_path))

    # print(tmp_df.head())
    # print(status)
    # print(error)

