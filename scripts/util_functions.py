from datetime import datetime, timedelta

import pandas as pd

def find_time_range(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')

    published_after = date_obj.strftime('%Y-%m-%dT00:00:00Z')
    published_before = (date_obj + timedelta(days=1) - timedelta(seconds=1)).strftime('%Y-%m-%dT23:59:59Z')

    return published_after, published_before