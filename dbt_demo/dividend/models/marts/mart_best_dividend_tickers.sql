with ranked as (

    select
        ticker,
        consistency_score,
        favorable_event_count,
        event_count,
        row_number() over (
            order by consistency_score desc, favorable_event_count desc, event_count desc, ticker
        ) as rank
    from {{ ref('int_ticker_dividend_stats') }}

)

select
    ticker,
    consistency_score,
    favorable_event_count,
    event_count,
    rank
from ranked
where rank <= 2
