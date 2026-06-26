{{ config(materialized='table') }}

with source as (
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
    from {{ source('bronze', 'game_logs') }}
),

with_cumulative as (
    select
        *,
        sum(is_win) over (
            partition by team_id, year
            order by game_date
            rows between unbounded preceding and current row
        ) as cumulative_wins,
        sum(is_loss) over (
            partition by team_id, year
            order by game_date
            rows between unbounded preceding and current row
        ) as cumulative_losses
    from source
)

select * from with_cumulative
