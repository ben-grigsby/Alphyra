import requests
import pandas as pd
import os

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
TICKER = 'NVDA'

url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={TICKER}&interval=5min&apikey={API_KEY}'


response = requests.get(url)
data = response.json()

print(data)