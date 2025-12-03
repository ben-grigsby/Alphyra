tech_master_symbol_set = set([
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AVGO", "CRM", "ORCL",
    "NOW", "SNOW", "DDOG", "MDB", "ZS", "CRWD", "OKTA", "NET", "HUBS", "PANW",
    "INTC", "AMD", "MU", "QCOM", "TXN", "IBM", "HPQ", "DELL", "STX", "WDC",
    "PATH", "AI", "PLTR", "RBLX", "IONQ", "U", "FSLY", "SMCI", "ARBE", "GLOB",
    "SQ", "PYPL", "AFRM", "COIN", "INTU", "ADP", "FISV", "BILL", "TWLO", "TTD"
])

company_info_metrics = [

    # Valuation
    
    'peTTM', # Price-to-Earnings (Trailing 12 Months)
    'pb', # Price-to-Book
    'psTTM', # Price-to-Sales (Trailing 12 Months)
    'pegTTM', # Price/Earnings-to-Growth (Trailing 12 Months)
    'marketCapitalization', # Total market value of the company
    'enterpriseValue', # Market cap + debt - cash

    # Profitability

    'grossMarginTTM', # Gross profit margin (Trailing 12 Months)
    'netProfitMarginTTM', # Net income margin (Trailing 12 Months)
    'operatingMarginTTM', # Operating margin (Trailing 12 Months)
    'roaTTM', # Return on Assets (Trailing 12 Months)
    'roeTTM', # Return on Equity (Trailing 12 Months)
    'roiTTM', # Return on Investment

    # Growth

    'revenueGrowthTTMYoy', # YoY revenue growth
    'epsGrowthTTMYoy', # YoY EPS growth
    'revenueGrowth5Y', # Revenue CAGR (5Y)
    'epsGrowth5Y', # EPS CAGR (5Y)

    # Financial Health

    'currentRatioQuarterly', # Ability to pay short-term liabilities
    'quickRatioQuarterly', # Conservative version of current ratio
    'totalDebt/totalEquityQuarterly', # Long-term debt risk
    'cashPerSharePerShareQuarterly', # Liquidity per share

    # Momentum

    '52WeekPriceReturnDaily', # 1-year price return
    '5DayPriceReturnDaily', # Short-term movement
    '13WeekPriceReturnDaily', # Quarterly return
    'priceRelativeToS&P50013Week', # Market-relative movement
]