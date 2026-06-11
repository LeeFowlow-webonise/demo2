from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine, text


def get_database_url() -> str:
    if url := os.getenv("DATABASE_URL"):
        return url

    user = os.getenv("DBT_POSTGRES_USER", "leefowlow")
    password = os.getenv("DBT_POSTGRES_PASSWORD", "")
    host = os.getenv("DBT_POSTGRES_HOST", "localhost")
    port = os.getenv("DBT_POSTGRES_PORT", "5432")
    database = os.getenv("DBT_POSTGRES_DB", "dbt_demo")

    if password:
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql+psycopg2://{user}@{host}:{port}/{database}"


def get_engine():
    return create_engine(get_database_url())


DDL = """
CREATE SCHEMA IF NOT EXISTS main_raw;

CREATE TABLE IF NOT EXISTS main_raw.dividend_events (
    ticker TEXT NOT NULL,
    ex_dividend_date DATE NOT NULL,
    dividend_amount NUMERIC(18, 6) NOT NULL,
    price_before NUMERIC(18, 6),
    price_on_ex NUMERIC(18, 6),
    price_drop NUMERIC(18, 6),
    drop_less_than_dividend BOOLEAN,
    loaded_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (ticker, ex_dividend_date)
);
"""


def create_tables(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text(DDL))


def replace_dividend_events(engine, frame: pd.DataFrame) -> int:
    create_tables(engine)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE main_raw.dividend_events"))
        frame.to_sql(
            "dividend_events",
            connection,
            schema="main_raw",
            if_exists="append",
            index=False,
            method="multi",
        )
    return len(frame)
