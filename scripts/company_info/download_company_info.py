import requests
import os

from dotenv import load_dotenv

load_dotenv()
FINNHUB_API = os.getenv("FINNHUB_API_KEY")


def get_company_info(symbol):
    """
    Retrieve company name and sector for a given stock symbol using Finnhub's profile2 endpoint.
    """
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get("name", None)
        sector = data.get("finnhubIndustry", None)
        return name, sector
    return None, None