import pandas as pd

from dividend_analysis.analysis import (
    build_dividend_events_frame,
    consistency_score,
    price_drop_on_ex_date,
)


def test_price_drop_less_than_dividend_when_drop_is_small():
    result = price_drop_on_ex_date(
        prices=pd.Series(
            {pd.Timestamp("2024-01-02"): 100.0, pd.Timestamp("2024-01-03"): 99.50}
        ),
        ex_dividend_date=pd.Timestamp("2024-01-03"),
        dividend_amount=1.00,
    )
    assert result["price_drop"] == 0.50
    assert result["drop_less_than_dividend"] is True


def test_price_drop_not_less_than_dividend_when_drop_is_large():
    result = price_drop_on_ex_date(
        prices=pd.Series(
            {pd.Timestamp("2024-01-02"): 100.0, pd.Timestamp("2024-01-03"): 98.00}
        ),
        ex_dividend_date=pd.Timestamp("2024-01-03"),
        dividend_amount=1.00,
    )
    assert result["price_drop"] == 2.00
    assert result["drop_less_than_dividend"] is False


def test_build_dividend_events_frame():
    dividends = pd.Series(
        {pd.Timestamp("2024-03-01"): 0.25},
    )
    prices = pd.Series(
        {
            pd.Timestamp("2024-02-29"): 50.0,
            pd.Timestamp("2024-03-01"): 49.90,
        }
    )
    frame = build_dividend_events_frame("AAA", dividends, prices)
    assert len(frame) == 1
    assert frame.loc[0, "drop_less_than_dividend"] == True


def test_consistency_score():
    frame = pd.DataFrame(
        {
            "drop_less_than_dividend": [True, True, False, True],
        }
    )
    assert consistency_score(frame) == 0.75
