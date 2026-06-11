#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datetime import date

from dividend_analysis.db import get_engine, replace_dividend_events
from dividend_analysis.loader import load_dividend_events_for_tickers
from dividend_analysis.ticker_sampling import sample_nasdaq_dividend_tickers


def main() -> None:
    last_year = date.today().year - 1
    tickers = sample_nasdaq_dividend_tickers(n=25, year=last_year, seed=42)
    print(f"Selected {len(tickers)} tickers: {', '.join(tickers)}")

    events = load_dividend_events_for_tickers(tickers, years=5)
    if events.empty:
        raise SystemExit("No dividend events were loaded.")

    row_count = replace_dividend_events(get_engine(), events)
    print(f"Loaded {row_count} rows into main_raw.dividend_events")


if __name__ == "__main__":
    main()
