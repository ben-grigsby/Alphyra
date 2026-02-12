import requests 
import pandas as pd
import os

from dotenv import load_dotenv

load_dotenv()
FINNHUB_API = os.getenv("FINNHUB_API_KEY")

def finnhub_news(symbol, from_date, to_date):
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API}"
    res = requests.get(url)

    if res.status_code == 200:
        return res.json()
    else:
        print(f"[ERROR] Error fetching news: {res.status_code}")
        return []



def get_peers(symbol):
    try:
        url = f"https://finnhub.io/api/v1/stock/peers?symbol={symbol}&token={FINNHUB_API}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to get peers for {symbol}: {e}")
        return []



if __name__ == '__main__':
    symbol = 'PLTR'
    from_date = '2025-01-01'
    to_date = '2025-01-20'

    news = finnhub_news(symbol, from_date, to_date)

    # if news:
    #     print(news[0])  # Print first article
    # else:
    #     print("No news found.")

    # peers = get_peers(symbol)

    # print(peers)