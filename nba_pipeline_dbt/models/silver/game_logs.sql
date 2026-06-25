{{ config(materialized='view') }}

with source as (
    select * from {{ source('bronze', 'game_logs') }}
)
select
    game_id,
    wl,
    year,
    season_id,
    team_id,
    team_abbreviation,
    team_name,
    game_date::date as game_date,
    case when wl = 'W' then 1 else 0 end as is_win,
    case when wl = 'L' then 1 else 0 end as is_loss
from source