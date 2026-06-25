{{ config(materialized='table') }}

with rule as (
    select * from {{ ref('rule_40_20') }}
),

champions as (
    select * from {{ ref('playoff_results') }}
    where playoff_round = 'Champion'
)

select
    c.year,
    c.team_name,
    c.team_id,
    c.wins,
    c.losses,
    c.po_wins,
    c.po_losses,
    r.achieved_40_20_rule,
    r.wins_at_20th_loss,
    r.date_of_20th_loss,
    case
        when r.achieved_40_20_rule then 'Satisfied the rule'
        else 'Exception - won without rule'
    end as rule_verdict
from champions c
left join rule r
    on c.team_id = r.team_id
    and c.year = r.year
order by c.year