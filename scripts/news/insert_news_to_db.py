import os
import pandas as pd
import json
import random

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from collections import deque
from datetime import datetime

from scripts.news.download_news import (
    finnhub_news,
    get_peers
)

from scripts.company_info.download_company_info import (
    get_company_info
)

from scripts.configuration import (
    tech_master_symbol_set
)

from scripts.analyze_db.database_functions import (
    get_db_info
)

load_dotenv()



def raw_news_JSON(symbol, from_date, to_date):
    """
    Retrieve raw news JSON for a given stock symbol over a specified date range.

    Parameters:
        symbol (str): The stock symbol to query (e.g., 'AAPL').
        from_date (str): Start date in 'YYYY-MM-DD' format.
        to_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        tuple: A tuple containing the raw JSON response and the associated symbol.
    """
    news_JSON = finnhub_news(symbol, from_date, to_date)

    return news_JSON, symbol



def transform_news(news_JSON, symbol, company_name, sector, existing_sources):
    """
    Transform a single news entry (in JSON format) into a structured Pandas DataFrame.

    Parameters:
        news_JSON (dict): A single news article in JSON format.
        symbol (str): The stock symbol associated with the news article.
        company_name (str): The company name.
        sector (str): The sector that the company is a part of.

    Returns:
        pd.DataFrame: A one-row DataFrame containing cleaned and structured news data.
    """
    if news_JSON['url'] in existing_sources:
        return None
    
    dt = datetime.fromtimestamp(news_JSON['datetime'])
    
    news_df = pd.DataFrame([{
        'company_name': company_name,
        'sector': sector,
        'symbol': symbol,
        'headline': news_JSON['headline'],
        'summary': news_JSON['summary'],
        'source': news_JSON['source'],
        'category': news_JSON['category'],
        'published_at': dt,
        'url': news_JSON['url'],
        'raw_json': json.dumps(news_JSON)
    }])

    return news_df



def get_url(query):
    df = get_db_info(query)

    inputted_news = df['url'].unique().tolist()

    return inputted_news



def insert_to_db(symbol, from_date, to_date, source_query):
    """
    Insert all news articles for a given symbol and date range into the Postgres database.

    Parameters:
        symbol (str): The stock symbol to fetch news for.
        from_date (str): Start date in 'YYYY-MM-DD' format.
        to_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        None
    """
    postgres_url = os.getenv("POSTGRES_URL")
    
    # print(postgres_url)

    engine = create_engine(postgres_url)

    rows = []
    raw_news = finnhub_news(symbol, from_date, to_date)
    company_name, sector = get_company_info(symbol)

    existing_sources = set(get_url(source_query))

    if not raw_news:
        print(f"No news for {symbol} from {from_date} to {to_date}")
        return False

    for entry in raw_news:
        df = transform_news(entry, symbol, company_name, sector, existing_sources)
        if df is None:
            continue
        
        rows.append(df)

    if rows:
        final_df = pd.concat(rows, ignore_index=True)
        final_df.to_sql('news', engine, schema='raw', if_exists='append', index=False)
        
        print(f"[INFO] Inserted {len(raw_news)} rows for {symbol} from {from_date} to {to_date}")
    
    else:
        print(f"[INFO] No insertion news for {symbol} from {from_date} to {to_date} was inserted.")

    return True



# def stock_researcher(stocks, from_date, to_date, n, source_query, peer_expansion=True):
    
    if isinstance(stocks, str):
        stocks = [stocks]

    if peer_expansion:
        queue = deque()
        visited = set()
        total = 0

        for stock in stocks:
            print(f"[INFO] Researching {stock}")

            visited.add(stock)

            if insert_to_db(stock, from_date, to_date, source_query):
                total += 1
                print(f"[INFO] Completed {stock} research")
                print(f"[INFO] Researched {total} stocks in total")
            else:
                print(f"[INFO] No news for {stock}")

            stock_peers = get_peers(stock)
            for peer in stock_peers:
                if peer not in visited and peer not in queue:
                    queue.append(peer)

        print("\n")
        print(f"[INFO] Starting research of peer stocks...")
        print("\n")

        while queue and len(visited) < n:
            curr_stock = queue.popleft()
            print(f"[INFO] Researching {curr_stock}")

            if insert_to_db(curr_stock, from_date, to_date, source_query):
                visited.add(curr_stock)
                total += 1
                print(f"[INFO] Completed {curr_stock} research")
                print(f"[INFO] Researched {total} stocks in total")
            else:
                print(f"[INFO] No news for {curr_stock}")

            stock_peers = get_peers(curr_stock)
            for peer in stock_peers:
                if peer not in visited and peer not in queue:
                    queue.append(peer)

        print(f"[INFO] Completed research for a total of {total} stocks")
    
    else:
        if insert_to_db(stocks[0], from_date, to_date, source_query):
            print(f"[INFO] Completed {stocks[0]} research")
        else:
            print(f"[INFO] No news for {stocks[0]}")


def stock_researcher(stocks, from_date, to_date, n, source_query, peer_expansion=True):
    if isinstance(stocks, str):
        stocks = [stocks]

    total = 0

    if not peer_expansion:
        for stock in stocks:
            if insert_to_db(stock, from_date, to_date, source_query):
                total += 1
            print(f"[INFO] Researched {total} stocks in total")
        return

    queue = deque()
    visited = set()

    for stock in stocks:
        visited.add(stock)
        if insert_to_db(stock, from_date, to_date, source_query):
            total += 1

        for peer in get_peers(stock):
            if peer not in visited and peer not in queue:
                queue.append(peer)

    print("\n[INFO] Starting research of peer stocks...\n")

    while queue and len(visited) < n:
        curr_stock = queue.popleft()
        visited.add(curr_stock)

        if insert_to_db(curr_stock, from_date, to_date, source_query):
            total += 1

        for peer in get_peers(curr_stock):
            if peer not in visited and peer not in queue:
                queue.append(peer)

    print(f"[INFO] Completed research for a total of {total} stocks")


if __name__ == '__main__':
    source_query = """
        SELECT 
            DISTINCT url
        FROM raw.news
    """
    stock_researcher(['PLTR', 'NVDA', 'AVGO'], '2025-11-17', '2025-11-21', 100, source_query, peer_expansion=False)