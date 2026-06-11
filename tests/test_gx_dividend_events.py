"""Great Expectations validation tests."""

from __future__ import annotations

import pandas as pd

from gx.validate_dividend_events import validate_dividend_events


def test_gx_validate_dividend_events():
    frame = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "ex_dividend_date": ["2024-01-01", "2024-04-01"],
            "dividend_amount": [0.5, 0.75],
        }
    )
    validate_dividend_events(frame)
