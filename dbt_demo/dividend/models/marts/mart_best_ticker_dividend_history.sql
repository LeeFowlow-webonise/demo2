select
    events.ticker,
    events.ex_dividend_date,
    events.dividend_amount,
    events.price_before,
    events.price_on_ex,
    events.price_drop,
    events.drop_less_than_dividend,
    best.rank,
    best.consistency_score
from {{ ref('stg_dividend_events') }} as events
inner join {{ ref('mart_best_dividend_tickers') }} as best
    on events.ticker = best.ticker
where events.ex_dividend_date >= current_date - interval '5 years'
order by best.rank, events.ex_dividend_date desc
