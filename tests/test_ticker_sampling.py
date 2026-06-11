from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from dividend_analysis.ticker_sampling import _paid_dividend_in_year, sample_nasdaq_dividend_tickers


def _mock_ticker_with_dividends(dividend_dates: list[str]) -> MagicMock:
    stock = MagicMock()
    stock.dividends = pd.Series(
        {pd.Timestamp(date, tz="UTC"): 0.25 for date in dividend_dates},
    )
    return stock


@patch("dividend_analysis.ticker_sampling.yf.Ticker")
def test_paid_dividend_in_year_true(mock_ticker):
    mock_ticker.return_value = _mock_ticker_with_dividends(["2024-03-01", "2024-09-01"])

    assert _paid_dividend_in_year("AAA", 2024) is True


@patch("dividend_analysis.ticker_sampling.yf.Ticker")
def test_paid_dividend_in_year_false_when_empty(mock_ticker):
    stock = MagicMock()
    stock.dividends = pd.Series(dtype=float)
    mock_ticker.return_value = stock

    assert _paid_dividend_in_year("AAA", 2024) is False


@patch("dividend_analysis.ticker_sampling._paid_dividend_in_year", return_value=True)
def test_sample_nasdaq_dividend_tickers_returns_sorted_sample(mock_paid):
    tickers = sample_nasdaq_dividend_tickers(n=3, year=2024, seed=42)

    assert len(tickers) == 3
    assert tickers == sorted(tickers)
    assert mock_paid.call_count > 0


@patch("dividend_analysis.ticker_sampling._paid_dividend_in_year", return_value=False)
def test_sample_nasdaq_dividend_tickers_raises_when_not_enough(mock_paid):
    with pytest.raises(ValueError, match="Only found 0 eligible tickers"):
        sample_nasdaq_dividend_tickers(n=25, year=2024)
