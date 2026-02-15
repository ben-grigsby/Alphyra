import os
import requests
import pandas as pd
import time

from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from requests.exceptions import SSLError, ConnectionError

from scripts.analyze_db.database_functions import (
    get_db_info,
    insert_historic_into_db
)

load_dotenv()  # Load API keys from .env

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")


headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

params = {
    "start": "2025-11-17",
    "end": "2025-11-21",
    "timeframe": "1Day"
}

response = requests.get(
    "https://data.alpaca.markets/v2/stocks/NVDA/bars",
    headers=headers,
    params=params
)



def safe_get(url, headers=None, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response
        
        except SSLError:
            print(f"[SSL ERROR] Retrying... attempt {attempt+1}/{max_retries}")
        
        except ConnectionError:
            print(f"[CONNECTION ERROR] Retrying... attempt {attempt+1}/{max_retries}")
        
        except Exception as e:
            print(f"[UNEXPECTED ERROR] {e}")
        
        time.sleep(1.5 * (attempt + 1))  # exponential backoff

    print("[ERROR] Max retries exceeded for URL:", url)
    return None



def get_next_monday(date_input):
    # Normalize input to a date object
    if isinstance(date_input, datetime):
        date_obj = date_input.date()
    elif isinstance(date_input, date):
        date_obj = date_input
    else:
        # assume string "YYYY-MM-DD"
        date_obj = datetime.strptime(date_input, "%Y-%m-%d").date()

    weekday = date_obj.weekday()  # Monday = 0
    days_until_next_monday = (7 - weekday) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7  # NEXT Monday, not today

    next_monday = date_obj + timedelta(days=days_until_next_monday)
    return next_monday.strftime("%Y-%m-%d")



def generate_week_ranges(num_weeks=52):
    today = datetime.today()

    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)

    for i in range(num_weeks):
        monday = current_monday - timedelta(weeks=i)
        friday = monday + timedelta(days=4)
        if monday > today or friday > today: 
            continue
        yield monday.strftime("%Y-%m-%d"), friday.strftime("%Y-%m-%d")



def get_news_stocks(query):
    stock_info = get_db_info(query)
    symbol_lst = stock_info['symbol'].unique().tolist()
    return symbol_lst



def get_stock_input_dates(query):
    info_date = get_db_info(query)
    date_lst = info_date['date'].unique().tolist()
    return date_lst



def get_stock_values(start, end, symbol, jump='1Day'):
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    params = {
        "start": start,
        "end": end,
        "timeframe": jump
    }

    response = safe_get(
    f"https://data.alpaca.markets/v2/stocks/{symbol}/bars",
    headers=headers,
    params=params
    )

    return response


def normalize_symbols(retrieve_all_stocks_query, stock=None):
    # If user did not specify a stock → get full list from DB
    if stock is None:
        df = get_db_info(retrieve_all_stocks_query)

        if df is None or "symbol" not in df.columns:
            return []

        symbols = df["symbol"].dropna().unique().tolist()
        return symbols
    
    # If stock is a single string → wrap it
    if isinstance(stock, str):
        return [stock]

    # If stock is already a list → return it
    if isinstance(stock, list):
        return stock
    
    raise ValueError("stock must be None, a string, or a list of strings.")



def fill_stock_values(retrieve_all_stocks_query, interval="1Day", stock=None):
    lst_symbols = normalize_symbols(retrieve_all_stocks_query, stock)
    
    for mon, fri in generate_week_ranges():
        print(f"\n---------------- {mon} -> {fri} ----------------\n")
        for symbol in lst_symbols:

            retrieve_stock_date_query = f"""
                SELECT date 
                FROM raw.stock_prices
                WHERE symbol = '{symbol}'
            """

            # Normalize existing dates → python date objects
            raw_dates = get_stock_input_dates(retrieve_stock_date_query)

            # print(raw_dates)

            if raw_dates:
                existing_dates = {
                    pd.to_datetime(d).date()
                    for d in get_stock_input_dates(retrieve_stock_date_query)
                }
            else:
                existing_dates = set()

            # Week date set
            mon_dt = pd.to_datetime(mon)
            mon_date = mon_dt.date()  

            fri_dt = pd.to_datetime(fri)
            fri_date = fri_dt.date()

            week_dates = {
                mon_date,
                mon_date + timedelta(days=1),
                mon_date + timedelta(days=2),
                mon_date + timedelta(days=3),
                mon_date + timedelta(days=4),
            }

            # Skip entire API call if fully populated
            if week_dates.issubset(existing_dates):
                print(f"[SKIP] All dates exist for {symbol} ({mon_date} -> {fri_date})")
                continue

            response = get_stock_values(mon, fri, symbol)
            if response is None:
                continue

            data = response.json()
            historic_values = data.get("bars", [])
            if not historic_values:
                print(f"[WARNING] No bars for {symbol} in {mon} -> {fri}")
                continue

            historic_records = []

            print(f"[INFO] Parsing {symbol} API response")

            for info in historic_values:
                bar_date = pd.to_datetime(info["t"]).date()

                # Skip existing daily rows
                if bar_date in existing_dates:
                    continue

                historic_records.append({
                    "symbol": symbol,
                    "date": bar_date,  # FIXED — correct normalized date
                    "open": info["o"],
                    "high": info["h"],
                    "low": info["l"],
                    "close": info["c"],
                    "volume": info["v"],
                })

            if not historic_records:
                print(f"[INFO] No new rows for {symbol} in {mon} -> {fri}")
                continue

            historic_df = pd.DataFrame(historic_records)

            insert_stat, error = insert_historic_into_db(historic_df)
            if insert_stat:
                print(f"[INFO] Inserted {len(historic_records)} rows for {symbol}")
            else:
                print(f"[ERROR] Insert failed for {symbol}. Error: {error}")



if __name__ == '__main__':
    query = "SELECT DISTINCT symbol FROM raw.news"

    fill_stock_values(query)