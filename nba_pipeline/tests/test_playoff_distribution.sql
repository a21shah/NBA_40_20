-- tests/test_playoff_distribution.sql
-- Ensure playoff results follow the standard bracket structure per year

with playoff_results as (
    select
        year,
        playoff_round,
        count(distinct team_id) as team_count
    from {{ ref('team_season_with_playoff_round') }}
    where playoff_round != 'Missed Playoffs'
    group by year, playoff_round
),

expected_counts as (
    select year, 'Champion' as playoff_round, 1 as expected_count from (select distinct year from {{ ref('team_season_with_playoff_round') }}) a
    union all
    select year, 'NBA Finals', 1 from (select distinct year from {{ ref('team_season_with_playoff_round') }}) a
    union all
    select year, 'Conference Finals', 2 from (select distinct year from {{ ref('team_season_with_playoff_round') }}) a
    union all
    select year, 'Second Round', 4 from (select distinct year from {{ ref('team_season_with_playoff_round') }}) a
    union all
    select year, 'First Round', 8 from (select distinct year from {{ ref('team_season_with_playoff_round') }}) a
),

validation_result as (
    select
        e.year,
        e.playoff_round,
        e.expected_count,
        coalesce(p.team_count, 0) as actual_count,
        case when e.expected_count = coalesce(p.team_count, 0) then 'PASS' else 'FAIL' end as result
    from expected_counts e
    left join playoff_results p
        on e.year = p.year
        and e.playoff_round = p.playoff_round
)

select * from validation_result where result = 'FAIL'