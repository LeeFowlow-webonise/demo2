with trips as (

    select * from {{ source('greenwheel', 'raw_trips') }}

),

bikes as (

    select * from {{ ref('stg_bikes') }}

),

joined as (

    select
        trips.bike_id,
        bikes.bike_model,
        trips.trip_cost,
        trips.trip_duration_seconds
    from trips
    inner join bikes
        on trips.bike_id = bikes.bike_id

)

select
    bike_id,
    bike_model,
    sum(trip_cost) as total_trip_cost,
    sum(trip_duration_seconds) / 60.0 as total_riding_minutes
from joined
group by 1, 2
