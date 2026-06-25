{{ config(materialized='view') }}

with team_history as (
    select distinct
        team_id,
        team_city,
        team_name,
        year as season
    from {{ source('bronze', 'team_season_stats') }}
),

with_changes as (
    select
        team_id,
        team_city,
        team_name,
        season,
        case
            when lag(team_name) over (partition by team_id order by season) != team_name
              or lag(team_city) over (partition by team_id order by season) != team_city
              or lag(team_name) over (partition by team_id order by season) is null
            then 1
            else 0
        end as is_new_identity
    from team_history
),

grouped as (
    select
        *,
        sum(is_new_identity) over (
            partition by team_id order by season
        ) as identity_group
    from with_changes
)

select
    team_id,
    team_city,
    team_name,
    min(season) as valid_from,
    max(season) as valid_to,
    max(season) = max(max(season)) over (partition by team_id) as is_current
from grouped
group by team_id, team_name, team_city, identity_group
order by team_id, valid_from