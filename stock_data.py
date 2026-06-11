from datetime import datetime, timedelta

import yfinance as yf


def fetch_last_week(ticker: str):
    end = datetime.now().date()
    start = end - timedelta(days=7)
    return yf.download(
        ticker.upper(),
        start=start,
        end=end + timedelta(days=1),
        progress=False,
    )


def get_close_prices(data):
    close = data["Close"]
    if hasattr(close, "squeeze"):
        close = close.squeeze()
    return close.dropna()
