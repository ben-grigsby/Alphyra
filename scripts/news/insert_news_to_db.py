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



def transform_news(news_JSON, symbol, company_name, sector):
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
    info = news_JSON
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



def insert_to_db(symbol, from_date, to_date):
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

    raw_news = finnhub_news(symbol, from_date, to_date)
    company_name, sector = get_company_info(symbol)

    if not raw_news:
        print(f"No news for {symbol} from {from_date} to {to_date}")
        return False

    for entry in raw_news:
        news_df = transform_news(entry, symbol, company_name, sector)
        news_df.to_sql('news', engine, schema='raw', if_exists='append', index=False)
    
    print(f"[INFO] Inserted {len(raw_news)} rows for {symbol} from {from_date} to {to_date}")

    return True



def stock_researcher(top_stocks, from_date, to_date, n):
    queue = deque()
    visited = set()
    total = 0

    for stock in top_stocks:
        print(f"[INFO] Researching {stock}")

        visited.add(stock)

        if insert_to_db(stock, from_date, to_date):
            total += 1
            print(f"[INFO] Completed {stock} research")
            print(f"[INFO] Researched {total} stocks in total")
        else:
            print(f"[INFO] No news for {stock}")

        stock_peers = get_peers(stock)
        for peer in stock_peers:
            if peer not in visited and peer not in queue and peer not in top_stocks:
                queue.append(peer)

    print("\n")
    print(f"[INFO] Starting research of peer stocks...")
    print("\n")

    while queue and len(visited) < n:
        curr_stock = queue.popleft()
        print(f"[INFO] Researching {curr_stock}")

        if insert_to_db(curr_stock, from_date, to_date):
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


if __name__ == '__main__':
    stock_researcher(tech_master_symbol_set, '2025-11-10', '2025-11-14', 100)