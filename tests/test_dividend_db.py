from __future__ import annotations

import pandas as pd
import pytest

from dividend_analysis.analysis import build_dividend_events_frame, consistency_score


def test_db_module_import():
    from dividend_analysis.db import get_database_url

    assert "postgresql" in get_database_url()


def test_get_database_url_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://user:pass@host:5432/db")
    from dividend_analysis.db import get_database_url

    assert get_database_url() == "postgresql+psycopg2://user:pass@host:5432/db"


def test_get_database_url_with_password(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DBT_POSTGRES_USER", "dbt")
    monkeypatch.setenv("DBT_POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("DBT_POSTGRES_HOST", "localhost")
    monkeypatch.setenv("DBT_POSTGRES_PORT", "5432")
    monkeypatch.setenv("DBT_POSTGRES_DB", "dbt_demo")
    from dividend_analysis.db import get_database_url

    assert get_database_url() == "postgresql+psycopg2://dbt:secret@localhost:5432/dbt_demo"


@pytest.mark.integration
def test_replace_dividend_events_round_trip():
    from dividend_analysis.db import get_engine, replace_dividend_events

    frame = pd.DataFrame(
        [
            {
                "ticker": "ZZZ",
                "ex_dividend_date": pd.Timestamp("2024-06-01").date(),
                "dividend_amount": 0.10,
                "price_before": 10.0,
                "price_on_ex": 9.95,
                "price_drop": 0.05,
                "drop_less_than_dividend": True,
            }
        ]
    )
    try:
        engine = get_engine()
        row_count = replace_dividend_events(engine, frame)
    except Exception as exc:
        pytest.skip(f"Postgres not available: {exc}")
        return

    assert row_count == 1


def test_build_empty_dividends_frame():
    frame = build_dividend_events_frame("AAA", pd.Series(dtype=float), pd.Series(dtype=float))
    assert frame.empty


def test_consistency_score_empty():
    assert consistency_score(pd.DataFrame(columns=["drop_less_than_dividend"])) is None
