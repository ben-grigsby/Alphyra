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



# def check_existing_video_id(new_video_zip, existing_video_zip_lst_set):
#     # zip = (symbol, video_id)
#     if new_video_zip in existing_video_zip_lst_set:
#         print(f"[INFO] Duplicate video for {new_video_zip[0]} encountered.")
#         return False
    
#     else:
#         return True



def edit_raw_videos(news_db_query, video_df_query, pub_after, pub_before):
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

    for stock in stocks_from_raw_news_set:
        print(f"Beginning {stock} video search for time interval {pub_after} - {pub_before}...")

        search_query = f"{stock} stock analysis"

        stock_video_ids_set = set(search_youtube_videos(search_query, pub_after, pub_before))

        if not stock_video_ids_set:
            print(f"[INFO] No videos found for {stock} from {pub_after} - {pub_before}")
            continue

        new_videos_set = stock_video_ids_set - processed_videos_id_set
        duplicate_videos_set = stock_video_ids_set & processed_videos_id_set

        df_lst = []


        for video_id in new_videos_set:
            print(f"[INFO] Registering {video_id} for {stock}")

            downloaded_video_info = get_video_details(video_id)

            if downloaded_video_info:
                print(f"Obtaining video info for {stock} video {video_id}...")

                transcript_path = f"downloads/{stock}/{id}"

                video_info_df = {
                    'symbol': stock,
                    'video_id': video_id,
                    'title': downloaded_video_info['title'],
                    'url': downloaded_video_info['url'],
                    'transcript_path': transcript_path,
                    'publish_date': downloaded_video_info['published_at'],
                    'is_copy': False
                }

                processed_videos_id_set.add(video_id)

                df_lst.append(video_info_df)
                processed_videos_df = pd.concat([processed_videos_df, video_info_df], ignore_index=True)

                print(f"[INFO] Appended {video_id} info for {stock} to df_lst")
            
            else:
                print(f"[ERROR] An error occurred when attempting to download {video_id} for {stock}")
                continue

        
        for video_id in duplicate_videos_set:
            print(f"[INFO] Copying {video_id} to {stock}")

            transcript_path = f"downloads/{stock}/{video_id}"

            video_info = processed_videos_df[processed_videos_df['video_id'] == video_id].iloc[[0]].copy()



def edit_raw_videos(news_db_query, video_df_query, pub_after, pub_before):
    print("Starting video search and download function...")

    pub_after = f"{pub_after}T00:00:00Z"
    pub_before = f"{pub_before}T23:59:59Z"

    existing_news_stocks = set(get_db_info(news_db_query)['symbol'].unique().tolist())
    all_existing_videos_info_df = get_db_info(video_df_query)
    existing_stock_video_tuple = set(
        tuple(x)
        for x in all_existing_videos_info_df[['symbol', 'video_id']].copy().itertuples(index=False)
    )
    existing_video_ids = {t[1] for t in existing_stock_video_tuple}

    df_lst = []
    lookup_df = []

    print(existing_news_stocks)

    for stock in existing_news_stocks:

        search_query = f"{stock} stock analysis"
        stock_video_ids_lst = search_youtube_videos(search_query, pub_after, pub_before)

        if not stock_video_ids_lst:
            print(f"No videos for {stock} from {pub_after} to {pub_before}, moving on...")
            continue

        symbol_id_zip = {(stock, id) for id in stock_video_ids_lst}
        new_video_ids = symbol_id_zip - existing_stock_video_tuple

        video_to_copy = {t[1] for t in new_video_ids if t[1] in existing_video_ids}
        video_to_download = {t[1] for t in new_video_ids if t[1] not in existing_video_ids}

        print(symbol_id_zip)

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
                    'publish_date': downloaded_video_info['published_at'],
                    'is_copy': False
                }

                video_info_df = pd.DataFrame([video_info_df])

                df_lst.append(video_info_df)
                lookup_df.append(video_info_df)
                print(f"Appended video {id} info to list of DataFrames")

                existing_video_ids.add(id)
                existing_stock_video_tuple.add((stock, id))
            
            else:
                continue

        
    if lookup_df:
        videos_to_download_df = pd.concat(lookup_df, ignore_index=True)
    else:
        videos_to_download_df = pd.DataFrame(columns=['video_id', 'title', 'url', 'publish_date'])


    for id in video_to_copy:
        print(f"Copying video id to be assigned to {stock}...")

        transcript_path = f"downloads/{stock}/{id}"

        if id in set(videos_to_download_df['video_id'].unique().tolist()):
            df_with_id = videos_to_download_df
        elif id in set(all_existing_videos_info_df['video_id'].unique().tolist()):
            df_with_id = all_existing_videos_info_df
        else:
            print(f"[WARN] No metadata found for video {id}, skipping copy")
            continue
        
        existing_video_df = (
            df_with_id
            .loc[df_with_id['video_id'] == id, ['title', 'url', 'publish_date']]
            .iloc[[0]]
            .copy()
        )

        existing_video_df['video_id'] = id
        existing_video_df['symbol'] = stock
        existing_video_df['transcript_path'] = transcript_path
        existing_video_df['is_copy'] = True


        df_lst.append(existing_video_df)

        existing_video_ids.add(id)
        existing_stock_video_tuple.add((stock, id))

        print(f"[INFO] Copied {len(video_to_copy)} existing videos for {stock}")

    
    if not df_lst:
        print(f"[INFO] No new videos to add")
        return False, "No new video records", None
    
    final_df = pd.concat(df_lst, ignore_index=True)

    if final_df.empty or final_df is None:
        return False, "Nothing to append to raw.videos"

    status, error = insert_video_into_db(final_df)
    
    return status, error, final_df



def download_and_process_videos(get_video_info_query, analyzed_videos_query):

    raw_videos_df = get_db_info(get_video_info_query)
    url_and_path = raw_videos_df[['symbol', 'url', 'transcript_path']]

    analyzed_videos_df = get_db_info(analyzed_videos_query)

    analyzed_videos_set = set(analyzed_videos_df['source_url'].unique().tolist())    
    videos_to_download_url_set = set(url_and_path['url'].unique().tolist())

    unseen_videos = videos_to_download_url_set - analyzed_videos_set

    # print(videos_to_download_url_set)
    # print(analyzed_videos_set)
    # print(unseen_videos)

    dedupe_mask = url_and_path['url'].apply(lambda x: x in unseen_videos)
    new_url_and_path = url_and_path[dedupe_mask]
    duplicate_videos = url_and_path[~dedupe_mask]

    for _, row in new_url_and_path.iterrows():
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
        else:
            print(f"[ERROR] Unable to delete file at {mp3_path}")
    
    right_df = get_db_info("""
        SELECT url, transcript_path 
        FROM raw.videos
    """)

    right_df = right_df.drop_duplicates(subset=['url'])

    acquire_old_transcript_path = (
        duplicate_videos
        .merge(
            right_df,
            on='url',
            how='left'
        )
    )
    
    return acquire_old_transcript_path



def analyze_video_sentiment(video_text_path):
    video_sentences = split_into_sentences(video_text_path)

    # print(video_sentences[0])

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




def compiler(news_db_query, video_df_query, pub_after, pub_before, get_video_info_query):
    video_search_status, video_search_error, video_search_df = edit_raw_videos(news_db_query, video_df_query, pub_after, pub_before)

    if video_search_status and video_search_error == None and not video_search_df.empty:
        print(f"[INFO] Successfully updated raw.videos dataframe to include new stock videos from {pub_after} to {pub_before}")
    elif video_search_status and video_search_error == None and video_search_df.empty:
        print(f"[INFO] No new rows added into raw.videos on account of empty DataFrame: {video_search_df.head()}")
    else:
        print(f"[ERROR] An error occurred when trying to update raw.videos. Status: {video_search_status}    Error: {video_search_error}")
        return False

    video_info = download_and_process_videos(get_video_info_query)

    return video_info

    # Work through the rows on of video_info and use the information provided to 



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
        SELECT * FROM raw.videos WHERE symbol = 'REMX'
    """
    analyzed_videos_query = """
        SELECT * FROM raw.sentiment WHERE stock_symbol = 'REMX'
    """

    pub_after = "2025-12-15"
    pub_before = "2025-12-19"

    output_dir = "downloads/transcriptions"

    lst_dfs = edit_raw_videos(news_query, all_video_query, pub_after, pub_before)
    print(lst_dfs)

    # print("ENTER __main__")

    # transcript_path = "downloads/REMX/IW-Mun1vEcE/transcript.txt"
    
    # # sentiment_df = combine_sentence_sentiment("downloads/REMX/IW-Mun1vEcE/transcript.txt")

    # video_df = download_and_process_videos(video_url_path_query, analyzed_videos_query)

    # print("FINAL OUTPUT: ")
    # print(video_df.head())

    # tmp_df, status, error = temp_insert_sentiment(combine_sentence_sentiment(transcript_path))

    # print(tmp_df.head())
    # print(status)
    # print(error)

