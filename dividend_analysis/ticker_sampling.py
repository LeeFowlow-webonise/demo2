from __future__ import annotations

from datetime import date, timedelta
import random

import pandas as pd
import yfinance as yf

from dividend_analysis.tickers import NASDAQ_DIVIDEND_CANDIDATES


def _paid_dividend_in_year(ticker: str, year: int) -> bool:
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if dividends.empty:
        return False

    start = pd.Timestamp(date(year, 1, 1), tz="UTC")
    end = pd.Timestamp(date(year + 1, 1, 1), tz="UTC")
    year_dividends = dividends[(dividends.index >= start) & (dividends.index < end)]
    return not year_dividends.empty


def sample_nasdaq_dividend_tickers(
    n: int = 25,
    year: int | None = None,
    seed: int = 42,
) -> list[str]:
    year = year or date.today().year - 1
    eligible = [ticker for ticker in NASDAQ_DIVIDEND_CANDIDATES if _paid_dividend_in_year(ticker, year)]
    if len(eligible) < n:
        raise ValueError(f"Only found {len(eligible)} eligible tickers for {year}, need {n}.")

    rng = random.Random(seed)
    return sorted(rng.sample(eligible, n))
