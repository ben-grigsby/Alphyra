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
        print(f"Error fetching news: {res.status_code}")
        return []



def get_peers(symbol, grouping=None):
    url = f"https://finnhub.io/api/v1/stock/peers?symbol={symbol}&token={FINNHUB_API}"

    if grouping:
        url += f"&grouping={grouping}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve peers for {symbol}")
        return []
    
    return response.json()



if __name__ == '__main__':
    symbol = 'AAPL'
    from_date = '2025-05-16'
    to_date = '2025-06-03'

    # news = finnhub_news(symbol, from_date, to_date)

    # if news:
    #     print(news[0])  # Print first article
    # else:
    #     print("No news found.")

    peers = get_peers(symbol)

    print(peers)