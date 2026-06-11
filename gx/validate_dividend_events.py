from __future__ import annotations

import pandas as pd
import great_expectations as ge


def validate_dividend_events(frame: pd.DataFrame) -> None:
    dataset = ge.from_pandas(frame)
    dataset.expect_column_values_to_not_be_null("ticker")
    dataset.expect_column_values_to_not_be_null("ex_dividend_date")
    dataset.expect_column_values_to_not_be_null("dividend_amount")
    dataset.expect_column_values_to_be_between("dividend_amount", min_value=0)
    dataset.expect_compound_columns_to_be_unique(["ticker", "ex_dividend_date"])

    results = dataset.validate()
    if not results["success"]:
        raise AssertionError(f"Great Expectations validation failed: {results}")


if __name__ == "__main__":
    sample = pd.DataFrame(
        {
            "ticker": ["AAA", "AAA"],
            "ex_dividend_date": ["2024-01-01", "2024-04-01"],
            "dividend_amount": [0.5, 0.5],
        }
    )
    validate_dividend_events(sample)
    print("Great Expectations validation passed.")
