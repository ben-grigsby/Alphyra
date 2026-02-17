import requests
import os
import json
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
FINNHUB_API = os.getenv("FINNHUB_API_KEY")

from scripts.company_info.sec_filings_analysis import (
    get_company_profile,
    extract_company_valuations,
    metric_period
)

from scripts.analyze_db.database_functions import (
    get_db_info,
    insert_financials_into_db
)


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




def get_company_financial_info(symbol):
    company_profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API}"
    comp_fin_url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API}"

    company_profile = get_company_profile(company_profile_url)
    metric_dict = extract_company_valuations(comp_fin_url)

    records = [
        {
            'symbol': symbol,
            'source': 'SEC 10-K',
            'metric_type': 'Balance Sheet',
            'metric_name': 'Shares Outstanding',
            'metric_period': 'Annual',
            'metric_value': company_profile['shareOutstanding'],
            'retrieved_at': datetime.now(),
            'raw_json': None
        }
    ] 

    for metric_name, metric_value in metric_dict.items():
        record = {
            'symbol': symbol,
            'source': 'finnhub',
            'metric_type': 'Valuation',  
            'metric_name': metric_name,
            'metric_period': metric_period(metric_name),
            'metric_value': metric_value,
            'retrieved_at': datetime.now(),
            'raw_json': None
        }
        records.append(record)

    return pd.DataFrame(records)



def get_company_financials(symbol, output_path="data/company_financials.txt"):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved financials for {symbol} to {output_path}")
    else:
        print(f"Failed to retrieve data for {symbol}: {response.status_code}")



def upload_company_financials(query):
    df = get_db_info(query)

    symbols = df['symbol'].unique().tolist()

    for symbol in symbols:
        symbol_df = get_company_financial_info(symbol)
        status, error = insert_financials_into_db(symbol_df)
        if status:
            print(f'[INFO] Successfully entered {symbol} financial information into table.')
        else:
            print(f'[ERROR] Unable to enter {symbol} financial information: {error}')


if __name__ == '__main__':
    # get_company_financial_info('GOOGL')
    query = "SELECT * FROM raw.news"
    upload_company_financials(query)