import pandas as pd
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

load_dotenv()

def insert_video_into_db(df):
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    try:
        df.to_sql('videos', engine, schema='raw', if_exists='append', index=False)
        return True, None
    except Exception as e:
        return False, e
