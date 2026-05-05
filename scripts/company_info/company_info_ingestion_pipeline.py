import requests
import os
import json
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
FINNHUB_API = os.getenv("FINNHUB_API_KEY")

from scripts.company_info.company_API_func import (
    get_company_profile,
    metric_period,
    extract_metric_and_series,
)

from scripts.analyze_db.database_functions import (
    get_db_info,
    insert_financials_into_db
)



def analyze_company_metrics_snapshot(symbol, metric_dict, snapshot_date, retrieved_at):
    records = []


    for metric_name, metric_value in metric_dict.items():
        # Skip non-numeric values
        if not isinstance(metric_value, (int, float)):
            continue
        
        record =  {
            'symbol': symbol,
            'source': 'finnhub',
            'metric_type': 'snapshot',  
            'metric_name': metric_name,
            'metric_period': metric_period(metric_name),
            'metric_value': metric_value,
            'snapshot_date': snapshot_date,
            'retrieved_at': retrieved_at,
            'financial_period_end': None,
            'raw_json': None
        }

        records.append(record)
    
    return pd.DataFrame(records)



def analyze_company_series(symbol, series_dict, retrieved_at):
    records = []

    annual_dict = series_dict.get('annual', {})
    quarterly_dict = series_dict.get('quarterly', {})

    for annual_key in annual_dict:
        for annual_value in annual_dict[annual_key]:

            period = annual_value['period']
            value = annual_value['v']

            record =  {
                'symbol': symbol,
                'source': 'finnhub',
                'metric_type': 'series',  
                'metric_name': annual_key,
                'metric_period': 'annual',
                'metric_value': value,
                'retrieved_at': retrieved_at,
                'snapshot_date': None,
                'financial_period_end': period,
                'raw_json': None
            }

            records.append(record)
    
    for quarterly_key in quarterly_dict:
        for quarterly_value in quarterly_dict[quarterly_key]:

            period = quarterly_value['period']
            value = quarterly_value['v']

            record =  {
                'symbol': symbol,
                'source': 'finnhub',
                'metric_type': 'series',  
                'metric_name': quarterly_key,
                'metric_period': 'quarterly',
                'metric_value': value,
                'retrieved_at': retrieved_at,
                'snapshot_date': None,
                'financial_period_end': period,
                'raw_json': None
            }

            records.append(record)
    
    return pd.DataFrame(records)



def analyze_company_profile(symbol, profile_dict, snapshot_date, retrieved_at):
    records = []

    for key in ['marketCapitalization', 'shareOutstanding']:
        value = profile_dict.get(key)
        if value is not None:
            record = {
                'symbol': symbol,
                'source': 'finnhub',
                'metric_type': 'snapshot',
                'metric_name': key,
                'metric_period': None,
                'metric_value': value,
                'retrieved_at': retrieved_at,
                'snapshot_date': snapshot_date,
                'financial_period_end': None,
                'raw_json': None
            }
    
            records.append(record)
    
    return pd.DataFrame(records)



def finance_dictionary_combinator(symbol):
    company_profile_dict = get_company_profile(symbol)
    market_snapshot_metrics, market_snapshot_series = extract_metric_and_series(symbol)

    snapshot_date = datetime.utcnow().date()
    retrieved_at = datetime.utcnow()

    symbol_series_df = analyze_company_series(symbol, market_snapshot_series, retrieved_at)
    symbol_metric_snapshot_df = analyze_company_metrics_snapshot(symbol, market_snapshot_metrics, snapshot_date, retrieved_at)
    symbol_company_profile = analyze_company_profile(symbol, company_profile_dict, snapshot_date, retrieved_at)

    combined_df = pd.concat([symbol_series_df, symbol_metric_snapshot_df, symbol_company_profile], ignore_index=True)

    return combined_df



def upload_company_financials(query):
    df = get_db_info(query)

    symbols = df['symbol'].unique().tolist()

    for symbol in symbols:
        symbol_company_df = finance_dictionary_combinator(symbol)
        status, error = insert_financials_into_db(symbol_company_df)
        if status:
            print(f'[INFO] Successfully entered {symbol} financial information into table.')
        else:
            print(f'[ERROR] Unable to enter {symbol} financial information: {error}')


if __name__ == '__main__':
    query = "SELECT * FROM raw.news WHERE symbol = 'NVDA'"
    upload_company_financials(query)
