import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prefect import flow, task

from stock_data import fetch_last_week, get_close_prices


@task(log_prints=True)
def fetch_stock_summary(ticker: str) -> dict:
    data = fetch_last_week(ticker)
    close = get_close_prices(data)

    if close.empty:
        raise ValueError(f"No price data found for ticker '{ticker}'.")

    latest_date = close.index[-1]
    latest_close = float(close.iloc[-1])
    summary = {
        "ticker": ticker.upper(),
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "latest_close": latest_close,
        "row_count": len(close),
    }
    print(summary)
    return summary


@flow(name="stock-price-check")
def stock_price_check(ticker: str = "AAPL") -> dict:
    return fetch_stock_summary(ticker)


if __name__ == "__main__":
    stock_price_check()
