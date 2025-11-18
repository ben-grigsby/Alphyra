from sqlalchemy import create_engine
from dotenv import load_dotenv

import os
import pandas as pd

load_dotenv()



def get_news_db(query):
    """
    Retrieve all news articles from the raw.news table in the PostgreSQL database.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all rows from the raw.news table, 
        ordered by symbol and published date.
    """
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    df = pd.read_sql(query, engine)
    return df



if __name__ == "__main__":
    symbol_list = get_news_db("SELECT * FROM raw.news")
    print(symbol_list[:5])