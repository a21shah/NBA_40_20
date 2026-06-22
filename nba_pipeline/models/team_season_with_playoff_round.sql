{{ config(schema='silver', materialized='view') }}

with source as (
    select * from {{ source('bronze', 'team_season_stats') }}
),

with_round as (
    select
        *,
        case
            when po_wins >= 15 and year < '2003-04' then 'Champion'
            when po_wins >= 11 and year < '2003-04' then 'NBA Finals'
            when po_wins >= 7 and year < '2003-04' then 'Conference Finals'
            when po_wins >= 3 and year < '2003-04' then 'Second Round'
            when po_wins >= 0 and po_losses = 3 and year < '2003-04' then 'First Round' --Prior to the 2003-04 season, the First Round was a best-of-five series
            when po_wins >= 16 and year >= '2003-04' then 'Champion'
            when po_wins >= 12 and year >= '2003-04' then 'NBA Finals'
            when po_wins >= 8 and year >= '2003-04' then 'Conference Finals'
            when po_wins >= 4 and year >= '2003-04' then 'Second Round'
            when po_wins >= 0 and po_losses = 4 and year >= '2003-04' then 'First Round' --Starting from the 2003-04 season, the First Round was a best-of-seven series
            else 'Missed Playoffs'
        end as playoff_round
    from source
    where year >= '1983-84' --The 193-84 season is when the NBA switched to its current 16-team playoff format establishing the four-round best-of-series knockout format
)

select * from with_round