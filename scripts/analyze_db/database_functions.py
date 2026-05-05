from sqlalchemy import create_engine
from dotenv import load_dotenv

import os
import pandas as pd

load_dotenv()



def get_db_info(query):
    """
    Retrieve data from a table in the PostgreSQL database.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all rows from a table, 
        ordered by symbol and published date.
    """
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    df = pd.read_sql(query, engine)
    return df



def insert_sentiment_into_db(df):
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    try:
        df.to_sql('sentiment', engine, schema='raw', if_exists='append', index=False)
        return True, None
    except Exception as e:
        return False, e



def insert_historic_into_db(df):
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    try:
        df.to_sql('stock_prices', engine, schema='raw', if_exists='append', index=False)
        return True, None
    except Exception as e:
        return False, e



def insert_financials_into_db(df):
    postgres_url = os.getenv("POSTGRES_URL")
    engine = create_engine(postgres_url)

    try:
        df.to_sql('company_financials', engine, schema='raw', if_exists='append', index=False)
        return True, None
    except Exception as e:
        return False, e



if __name__ == "__main__":
    query = "SELECT * FROM raw.news"
    symbol_list = get_db_info(query)
    print(symbol_list[:5])