{{ config(schema='gold', materialized='table') }}

with game_logs as (
    select * from {{ ref('game_logs_with_cumulative_win_loss') }}
),

twentieth_loss as (
    select
        team_id,
        team_name,
        year,
        min(game_date) as date_of_20th_loss,
        min(cumulative_wins) as wins_at_20th_loss
    from game_logs
    where cumulative_losses = 20
    group by team_id, team_name, year
),

final_record as (
    select
        team_id,
        team_name,
        year,
        max(cumulative_wins) as final_wins,
        max(cumulative_losses) as final_losses,
        max(cumulative_wins) + max(cumulative_losses) as games_played
    from game_logs
    group by team_id, team_name, year
)

select
    f.team_id,
    f.team_name,
    f.year,
    f.final_wins,
    f.final_losses,
    f.games_played,
    t.date_of_20th_loss,
    t.wins_at_20th_loss,
    case
        when t.wins_at_20th_loss is null then true
        when t.wins_at_20th_loss >= 40 then true
        else false
    end as achieved_40_20_rule
from final_record f
left join twentieth_loss t
    on f.team_id = t.team_id
    and f.year = t.year