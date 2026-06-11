with events as (

    select * from {{ ref('stg_dividend_events') }}
    where ex_dividend_date >= current_date - interval '5 years'

),

last_year as (

    select *
    from events
    where ex_dividend_date >= date_trunc('year', current_date - interval '1 year')
      and ex_dividend_date < date_trunc('year', current_date)

),

last_year_stats as (

    select
        ticker,
        count(*) as last_year_event_count,
        sum(case when drop_less_than_dividend then 1 else 0 end) as last_year_favorable_count
    from last_year
    group by 1

),

five_year_stats as (

    select
        ticker,
        count(*) as event_count,
        sum(case when drop_less_than_dividend then 1 else 0 end) as favorable_event_count,
        avg(case when drop_less_than_dividend then 1.0 else 0.0 end) as consistency_score
    from events
    group by 1

)

select
    five_year_stats.ticker,
    five_year_stats.event_count,
    five_year_stats.favorable_event_count,
    five_year_stats.consistency_score,
    coalesce(last_year_stats.last_year_event_count, 0) as last_year_event_count,
    coalesce(last_year_stats.last_year_favorable_count, 0) as last_year_favorable_count
from five_year_stats
inner join last_year_stats
    on five_year_stats.ticker = last_year_stats.ticker
where last_year_stats.last_year_favorable_count > 0
