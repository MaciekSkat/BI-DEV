select
    s.item_id,
    s.store_id,
    s.dept_id,
    c.calendar_date       as sale_date,
    c.day_of_week_num,
    s.units_sold
from {{ ref('sales_long') }} s
inner join {{ ref('stg_calendar') }} c
    on s.d = c.day_id