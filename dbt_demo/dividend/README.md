# Dividend Analysis Project

## 1. Load market data (Python + yfinance)

```bash
# Real data (25 random Nasdaq dividend tickers, 5 years history)
export DATABASE_URL=postgresql+psycopg2://dbt:dbt@localhost:5432/dbt_demo  # Docker Postgres
python scripts/load_dividend_data.py

# Deterministic fixture (CI / local dbt dev)
python scripts/load_dividend_fixture.py
```

Creates `main_raw.dividend_events` with columns:
`ticker`, `ex_dividend_date`, `dividend_amount`, `price_before`, `price_on_ex`, `price_drop`, `drop_less_than_dividend`

## 2. Run dbt models

```bash
cd dbt_demo/dividend
dbt deps --profiles-dir ../../docker/dbt
dbt build --profiles-dir ../../docker/dbt
```

Models:
- `stg_dividend_events` — cleaned source
- `int_ticker_dividend_stats` — 5-year consistency score
- `mart_best_dividend_tickers` — top 2 tickers
- `mart_best_ticker_dividend_history` — dividend history for top 2 (max 5 years)

## 3. Tests

```bash
pytest tests/ --cov=dividend_analysis --cov=gx --cov-report=term-missing
python gx/validate_dividend_events.py
cd dbt_demo/dividend && dbt test --profiles-dir ../../docker/dbt
```

## 4. CI

GitHub Actions workflow `.github/workflows/ci.yml` runs Python tests + coverage, GX validation, fixture load, and `dbt build`.
