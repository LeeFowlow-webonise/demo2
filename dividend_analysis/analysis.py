from __future__ import annotations

from datetime import date

import pandas as pd


def previous_trading_day(prices: pd.Series, event_day: pd.Timestamp) -> pd.Timestamp | None:
    prior = prices.index[prices.index < event_day]
    if prior.empty:
        return None
    return prior[-1]


def price_drop_on_ex_date(
    prices: pd.Series,
    ex_dividend_date: pd.Timestamp,
    dividend_amount: float,
) -> dict:
    if ex_dividend_date not in prices.index:
        return {
            "price_before": None,
            "price_on_ex": None,
            "price_drop": None,
            "drop_less_than_dividend": None,
        }

    before_day = previous_trading_day(prices, ex_dividend_date)
    if before_day is None:
        return {
            "price_before": None,
            "price_on_ex": None,
            "price_drop": None,
            "drop_less_than_dividend": None,
        }

    price_before = float(prices.loc[before_day])
    price_on_ex = float(prices.loc[ex_dividend_date])
    price_drop = price_before - price_on_ex

    return {
        "price_before": price_before,
        "price_on_ex": price_on_ex,
        "price_drop": price_drop,
        "drop_less_than_dividend": price_drop < dividend_amount,
    }


def build_dividend_events_frame(
    ticker: str,
    dividends: pd.Series,
    prices: pd.Series,
    start_date: date | None = None,
    end_date: date | None = None,
) -> pd.DataFrame:
    if dividends.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "ex_dividend_date",
                "dividend_amount",
                "price_before",
                "price_on_ex",
                "price_drop",
                "drop_less_than_dividend",
            ]
        )

    rows: list[dict] = []
    for ex_date, amount in dividends.items():
        ex_day = pd.Timestamp(ex_date.date())
        if start_date and ex_day.date() < start_date:
            continue
        if end_date and ex_day.date() > end_date:
            continue

        metrics = price_drop_on_ex_date(prices, ex_day, float(amount))
        rows.append(
            {
                "ticker": ticker,
                "ex_dividend_date": ex_day.date(),
                "dividend_amount": float(amount),
                **metrics,
            }
        )

    return pd.DataFrame(rows)


def consistency_score(events: pd.DataFrame) -> float | None:
    valid = events.dropna(subset=["drop_less_than_dividend"])
    if valid.empty:
        return None
    return float(valid["drop_less_than_dividend"].mean())
