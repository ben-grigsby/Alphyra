import requests 
import re
import json


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