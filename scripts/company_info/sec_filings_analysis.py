import requests 
import re

# from bs4 import BeautifulSoup

from scripts.configuration import (
    company_info_metrics
)



def extract_shares_outstanding(report_url):
    try:
        shares_outstanding_label = "us-gaap_CommonStockSharesOutstanding"
        response = requests.get(report_url)
        data = response.json()

        most_recent = data['data'][0]
        filed_date = most_recent['filedDate']
        fiscal_year = (most_recent['startDate'], most_recent['endDate'])
        so_value = None

        # print(filed_date, fiscal_year)

        print(f"[INFO] Parsing for Shares Outstanding Value")
        for value in most_recent['report']['bs']:
            if value['concept'] == shares_outstanding_label:
                so_value = value['value']

            # if value['concept'] == shares_outstanding_label:
            #     so_value = value['value']
                
            #     printå(f"[INFO] Retrieved shares outstanding.")
            #     return so_value, filed_date, fiscal_year
            # else:
            #     continue
                print(f"[INFO] Successfully found shares oustanding value.")
                return so_value, filed_date, fiscal_year
        
    except Exception as e:
        print(f"[ERROR] Unable to parse for shares outstanding: {e}")
    
    return None, None, None



def extract_company_valuations(filing_url):
    try:
        value_metrics = company_info_metrics
        response = requests.get(filing_url)
        data = response.json()
        metrics = data['metric']

        metric_dict = {}

        for key, value in metrics.items():
            if key in value_metrics:
                print(f"[INFO] Adding {key} to records.")
                metric_dict[key] = value
        
        return metric_dict
    
    except Exception as e:
        print(f'[ERROR] Unable to locate all desired metrics: {e}')

    return {}



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