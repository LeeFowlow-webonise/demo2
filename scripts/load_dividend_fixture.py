#!/usr/bin/env python3
"""Load deterministic fixture data for CI and local dbt development."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from dividend_analysis.db import get_engine, replace_dividend_events


def build_fixture_frame() -> pd.DataFrame:
    rows = []
    for ticker, score_bias in [("AAA", True), ("BBB", True), ("CCC", False)]:
        for year_offset, month in [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)]:
            ex_date = pd.Timestamp(year=2026 - year_offset, month=month, day=15).date()
            dividend_amount = 1.0
            price_drop = 0.5 if score_bias else 1.5
            rows.append(
                {
                    "ticker": ticker,
                    "ex_dividend_date": ex_date,
                    "dividend_amount": dividend_amount,
                    "price_before": 100.0,
                    "price_on_ex": 100.0 - price_drop,
                    "price_drop": price_drop,
                    "drop_less_than_dividend": price_drop < dividend_amount,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    frame = build_fixture_frame()
    count = replace_dividend_events(get_engine(), frame)
    print(f"Loaded {count} fixture rows into main_raw.dividend_events")


if __name__ == "__main__":
    main()
