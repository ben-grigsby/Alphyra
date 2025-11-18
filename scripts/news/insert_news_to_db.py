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
    
    print(f"Inserted {len(raw_news)} rows for {symbol} from {from_date} to {to_date}")

    return True



def retrieve_chain_symbols(base_symbol, from_date, to_date, n):
    """
    Recursively retrieve and insert news data for a base stock symbol and its peers.

    Limits insertion to 10 unique symbols to avoid excessive API usage or DB overload.

    Parameters:
        base_symbol (str): The starting stock symbol (e.g., 'AAPL').
        from_date (str): Start date in 'YYYY-MM-DD' format.
        to_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        None
    """
    visited = set()        # all symbols we attempted
    successful = set()     # symbols with actual news
    queue = deque()

    initial_peers = get_peers(base_symbol)
    queue.extend(initial_peers)
    queue.append(base_symbol)

    while queue and len(successful) < n:
        symbol = queue.popleft()
        
        if symbol in visited:
            continue

        visited.add(symbol)
        print(f"[INFO] Checking {symbol}")

        # Try inserting
        news_exists = insert_to_db(symbol, from_date, to_date)

        if news_exists:
            successful.add(symbol)

            # Only expand network **if symbol had news**
            new_peers = get_peers(symbol)
            for peer in new_peers:
                if peer not in visited:
                    queue.append(peer)

            print(f"[INFO] Added {symbol} to successful list ({len(successful)})")
        else:
            print(f"[INFO] No news for {symbol}, ignoring.")

    return successful



def master_symbol_safety(from_date, to_date, n, symbol=None):
    visited = set()

    if symbol:
        visited.update(retrieve_chain_symbols(symbol, from_date, to_date, n))
    else:
        random_init = random.choice(list(tech_master_symbol_set))
        visited.update(retrieve_chain_symbols(random_init, from_date, to_date, n))

    while len(visited) < n:
        remaining_symbols = tech_master_symbol_set - visited
        if not remaining_symbols:
            print("[INFO] Exhausted master symbol list.")
            break

        random_symbol = random.choice(list(remaining_symbols))
        new_visited = retrieve_chain_symbols(random_symbol, from_date, to_date, n)
        visited.update(new_visited)

    print(f"[INFO] Collected news for {len(visited)} unique symbols.")
    return visited
        


if __name__ == '__main__':
    master_symbol_safety("2025-11-10", "2025-11-14", 100, 'NVDA')