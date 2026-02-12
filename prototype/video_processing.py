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

    print(acquire_old_transcript_path)
    
   return acquire_old_transcript_path

