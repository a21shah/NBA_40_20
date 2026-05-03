CREATE TABLE IF NOT EXISTS BRONZE.team_season_stats (
    YEAR varchar(10),
    TEAM_ID int,
    TEAM_CITY varchar(25),
    TEAM_NAME varchar(25),
    GP int,
    WINS int,
    LOSSES int,
    CONF_RANK int,
    CONF_COUNT decimal,
    PO_WINS int,
    PO_LOSSES int,
    NBA_FINALS_APPEARANCE varchar(20),
    CONSTRAINT PK_team_season_stats_year_team_id PRIMARY KEY (YEAR, TEAM_ID)
)