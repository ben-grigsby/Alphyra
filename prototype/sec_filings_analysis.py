import requests 
import re
import json

from dotenv import load_dotenv

load_dotenv()
FINNHUB_API = os.getenv("FINNHUB_API_KEY")


# from bs4 import BeautifulSoup

from scripts.configuration import (
    company_info_metrics
)



def get_company_profile(report_url):
    try:
        response = requests.get(report_url)
        
        data = response.json()

        # filename = "sec_debug_report.json"

        # with open(filename, 'w') as f:
        #     json.dump(data, f, indent=2)

        print(f"[INFO] Successfully acquired company profile from API...")
        
        return data
        
    except Exception as e:
        print(f"[ERROR] Unable to acquire company profile information: {e}")
        

def extract_metric_and_series(symbol):
    market_snapshot_url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API}"

    try:
        response = requests.get(market_snapshot_url)
        response.raise_for_status()

        data = response.json()

        metrics = data.get('metric', {})
        series = data.get('series', {})

        return metrics, series

    except Exception as e:
        print(f'[ERROR] Failed extracting metric and series: {e}')
        return {}, {}


def metric_period(metric_name):
    if 'Yoy' in metric_name:
        return 'YoY'
    elif 'TTM' in metric_name:
        return 'TTM'
    elif '5Y' in metric_name:
        return '5Y'
    elif 'Quarterly' in metric_name:
        return 'Q'
    elif '52Week' in metric_name:
        return '52W'
    elif '5Day' in metric_name:
        return '5D'
    elif '13Week' in metric_name:
        return '13W'
    else:
        return None



if __name__ == '__main__':
    pass