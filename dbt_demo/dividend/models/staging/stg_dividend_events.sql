select
    ticker,
    ex_dividend_date,
    dividend_amount,
    price_before,
    price_on_ex,
    price_drop,
    drop_less_than_dividend
from {{ source('dividend_raw', 'dividend_events') }}
where price_drop is not null
  and drop_less_than_dividend is not null
