CREATE SCHEMA IF NOT EXISTS BRONZE;

CREATE TABLE IF NOT EXISTS BRONZE.game_logs (
    YEAR varchar(10),
    SEASON_ID varchar(20), 
    TEAM_ID int, 
    TEAM_ABBREVIATION varchar(10), 
    TEAM_NAME varchar(50), 
    GAME_ID varchar(30),
    GAME_DATE date,
    WL varchar(10),
    CONSTRAINT PK_game_logs_team_id_game_id PRIMARY KEY (TEAM_ID, GAME_ID)
)