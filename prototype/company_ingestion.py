def get_company_financial_info(symbol):
    company_profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API}"
    market_snapshot_url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API}"

    company_profile = get_company_profile(company_profile_url)
    metric_snapshot_dict, series_snapshot_dict = extract_metric_and_series(market_snapshot_url)

    snapshot_date = datetime.utcnow().date()
    retrieved_at = datetime.utcnow()    

    print(company_profile)

    records = [
        {
            'symbol': symbol,
            'source': 'SEC 10-K',
            'metric_type': 'snapshot',
            'metric_name': 'Shares Outstanding',
            'metric_period': 'Annual',
            'metric_value': company_profile['shareOutstanding'],
            'retrieved_at': datetime.now(),
            'raw_json': None
        }
    ] 

    for metric_name, metric_value in metric_snapshot_dict.items():
        record = {
            'symbol': symbol,
            'source': 'finnhub',
            'metric_type': 'snapshot',  
            'metric_name': metric_name,
            'metric_period': metric_period(metric_name),
            'metric_value': metric_value,
            'financial_date': snapshot_date,
            'retrieved_at': retrieved_at,
            'financial_period_end': None,
            'raw_json': None
        }
        records.append(record)

    return pd.DataFrame(records)



def get_company_financials(symbol, output_path="data/GOOGL_market_snapshot.txt"):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={FINNHUB_API}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved financials for {symbol} to {output_path}")
    else:
        print(f"Failed to retrieve data for {symbol}: {response.status_code}")



def get_company_profile(symbol, output_path="data/GOOGL_company_profile.txt"):
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={FINNHUB_API}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Saved financials for {symbol} to {output_path}")
    else:
        print(f"Failed to retrieve data for {symbol}: {response.status_code}")