{{ config(schema='gold', materialized='view') }}

select * from {{ ref('team_season_with_playoff_round') }}
where year not in ('1998-99', '2011-12') --remove lockout seasons as 98-99 had 50 games and 11-12 had 66 games