from datetime import datetime, timedelta

import pandas as pd
import os

def find_time_range(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    published_after = date_obj.strftime('%Y-%m-%dT00:00:00Z')
    published_before = (date_obj + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')

    return published_after, published_before



def get_week_range(date_obj):
    # date_obj is already a datetime.date
    monday = date_obj - timedelta(days=date_obj.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday



def save_processed_id(video_id, path="data/processed_videos.txt"):
    with open(path, "a") as f:
        f.write(f"{video_id}\n")



def load_processed_ids(path="data/processed_videos.txt"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(line.strip() for line in f)
    return set()



def val_in_list_mask_df(df, col, lst):
    df_mask = df[col].apply(lambda x: x in lst)
    new_df = df[df_mask]

    return new_df