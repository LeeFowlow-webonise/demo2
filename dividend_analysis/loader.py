from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from dividend_analysis.analysis import build_dividend_events_frame


def fetch_ticker_history(ticker: str, years: int = 5) -> tuple[pd.Series, pd.Series]:
    end = date.today() + timedelta(days=1)
    start = date.today() - timedelta(days=365 * years + 30)
    history = yf.download(
        ticker,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True,
    )
    if history.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    close = history["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.squeeze()
    close.index = pd.to_datetime(close.index).tz_localize(None).normalize()

    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if not dividends.empty:
        dividends.index = pd.to_datetime(dividends.index).tz_convert(None).normalize()
    return dividends, close


def load_dividend_events_for_tickers(
    tickers: list[str],
    years: int = 5,
) -> pd.DataFrame:
    start_date = date.today() - timedelta(days=365 * years)
    frames: list[pd.DataFrame] = []

    for ticker in tickers:
        dividends, prices = fetch_ticker_history(ticker, years=years)
        frame = build_dividend_events_frame(
            ticker=ticker,
            dividends=dividends,
            prices=prices,
            start_date=start_date,
        )
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
