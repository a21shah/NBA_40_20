{{ config(schema='silver', materialized='table') }}

with source as (
    select * from {{ ref('game_logs') }}
),

with_cumulative as (
    select
        *,
        sum(is_win) over (
            partition by team_id, season
            order by game_date
            rows between unbounded preceding and current row
        ) as cumulative_wins,
        sum(is_loss) over (
            partition by team_id, season
            order by game_date
            rows between unbounded preceding and current row
        ) as cumulative_losses
    from source
)

select * from with_cumulative