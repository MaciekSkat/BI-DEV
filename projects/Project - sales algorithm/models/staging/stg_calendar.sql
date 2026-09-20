-- test CI check
select
    [date]      as calendar_date,
    d           as day_id,
    wm_yr_wk    as week_id,
    weekday     as day_name,
    wday        as day_of_week_num,
    month       as month_num,
    [year]      as year_num,
    event_name_1,
    event_type_1,
    event_name_2,
    event_type_2,
    snap_CA     as is_snap_ca,
    snap_TX     as is_snap_tx,
    snap_WI     as is_snap_wi
from {{ ref('calendar') }}