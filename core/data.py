import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_price_data(tickers, period_years=2):
    """
    Fetch adjusted close price data for given tickers.
    Default: last 2 years
    """

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * period_years)

    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=False
    )

    if data.empty:
        raise ValueError("No data returned from Yahoo Finance.")

    # Use Adjusted Close
    if "Adj Close" in data.columns:
        data = data["Adj Close"]
    else:
        data = data["Close"]

    data = data.ffill().bfill()
    return data