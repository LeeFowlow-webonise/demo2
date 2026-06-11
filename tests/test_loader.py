from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

from dividend_analysis.loader import fetch_ticker_history, load_dividend_events_for_tickers


@patch("dividend_analysis.loader.yf.Ticker")
@patch("dividend_analysis.loader.yf.download")
def test_fetch_ticker_history_returns_empty_when_no_prices(mock_download, mock_ticker):
    mock_download.return_value = pd.DataFrame()

    dividends, prices = fetch_ticker_history("AAA")

    assert dividends.empty
    assert prices.empty
    mock_ticker.assert_not_called()


@patch("dividend_analysis.loader.yf.Ticker")
@patch("dividend_analysis.loader.yf.download")
def test_fetch_ticker_history_normalizes_prices_and_dividends(mock_download, mock_ticker):
    mock_download.return_value = pd.DataFrame(
        {"Close": [100.0, 99.5]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )
    mock_stock = MagicMock()
    mock_stock.dividends = pd.Series(
        {pd.Timestamp("2024-01-03", tz="America/New_York"): 0.50},
    )
    mock_ticker.return_value = mock_stock

    dividends, prices = fetch_ticker_history("AAA", years=1)

    assert len(dividends) == 1
    assert dividends.index.tz is None
    assert prices.loc[pd.Timestamp("2024-01-03")] == 99.5


@patch("dividend_analysis.loader.yf.Ticker")
@patch("dividend_analysis.loader.yf.download")
def test_fetch_ticker_history_squeezes_multi_column_close(mock_download, mock_ticker):
    idx = pd.to_datetime(["2024-02-29", "2024-03-01"])
    history = pd.DataFrame({("Close", "AAA"): [50.0, 49.9]}, index=idx)
    history.columns = pd.MultiIndex.from_tuples([("Close", "AAA")])
    mock_download.return_value = history
    mock_stock = MagicMock()
    mock_stock.dividends = pd.Series(dtype=float)
    mock_ticker.return_value = mock_stock

    _, prices = fetch_ticker_history("AAA")

    assert isinstance(prices, pd.Series)
    assert len(prices) == 2


@patch("dividend_analysis.loader.fetch_ticker_history")
def test_load_dividend_events_for_tickers_concatenates_frames(mock_fetch):
    dividends = pd.Series({pd.Timestamp("2024-03-01"): 0.25})
    prices = pd.Series(
        {
            pd.Timestamp("2024-02-29"): 50.0,
            pd.Timestamp("2024-03-01"): 49.90,
        }
    )
    mock_fetch.return_value = (dividends, prices)

    frame = load_dividend_events_for_tickers(["AAA", "BBB"], years=5)

    assert len(frame) == 2
    assert set(frame["ticker"]) == {"AAA", "BBB"}
    assert mock_fetch.call_count == 2


def test_load_dividend_events_for_tickers_empty_list():
    frame = load_dividend_events_for_tickers([], years=5)
    assert frame.empty
