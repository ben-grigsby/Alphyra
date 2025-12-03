import os
import requests
import pandas as pd

from dotenv import load_dotenv

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

def get_historic_data(query, start, end, timeframe):
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    params = {
        "start": start,
        "end": end,
        "timeframe": timeframe
    }

    stock_info = get_db_info(query)
    symbol_lst = stock_info['symbol'].unique().tolist()

    # i = 0

    for symbol in symbol_lst:
        # if i == 1:
        #     break 

        print(f"[INFO] Retrieving historic stock information for {symbol}")

        response = requests.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/bars",
            headers=headers,
            params=params
        )

        data = response.json()

        historic_records = []

        historic_values = data['bars']

        print(f"[INFO] Parsing through {symbol} API response")
        for info in historic_values:
            historic_records.append({
                'symbol': symbol,
                'date': info['t'],
                'open': info['o'],
                'high': info['h'],
                'low': info['l'],
                'close': info['c'],
                'volume': info['v'],
                # weighted_volume = info['wv']
            })
        
        historic_df = pd.DataFrame(historic_records)
        
        insert_stat, error = insert_historic_into_db(historic_df)

        if insert_stat:
            print(f"[INFO] Successfully inserted {symbol} historic stock prices into database")
        else:
            print(f"[ERROR] Unable to insert video {id} into database. Error: {error}")

        # i += 1

# print(response.json())

if __name__ == '__main__':
    query = "SELECT DISTINCT symbol FROM raw.news"
    get_historic_data(query, "2025-11-17", "2025-11-21", "1Day")