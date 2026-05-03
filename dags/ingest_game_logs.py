import datetime
from airflow.sdk import dag, task, get_current_context
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.library.parameters import SeasonTypeAllStar
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from time import sleep

@dag(
    dag_id="nba_game_logs",
    schedule=None,
    start_date=datetime.datetime(2026, 3, 17),
    catchup=False,
    tags=["Game Logs"],
)
def workflow():

    @task()
    def api_get_game_logs():
        context = get_current_context()
        
        seasons = []
        for year in range(1983, 2025):
            season = f'{str(year)}-{str(year+1)[-2:]}'
            seasons.append(season)
        
        season_override = context['dag_run'].conf.get('season', None)
        if season_override:
            seasons = [season_override]
        
        cols = ['YEAR', 'SEASON_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'WL']
        df_final = pd.DataFrame()
        for season in seasons:
            print(f'Getting data for the {season} NBA Season')
            
            gl = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star=SeasonTypeAllStar.regular,
                timeout=60,
            )

            df = gl.get_data_frames()[0]
            df['YEAR'] = season
            df = df[cols]
            
            print(f'The {season} Season has {df.shape[0]} regular season games')
            
            df_final = pd.concat([df_final, df])
            sleep(3)
        
        return df_final

    @task()
    def postgres_insert_data(df):
        conn = psycopg2.connect(
            host='postgres',
            port='5432',
            dbname='nba_db',
            user='airflow',
            password='airflow'
        )

        rows = list(df.itertuples(index=False, name=None))
        columns = ','.join(list(df.columns.to_list()))
        table = 'BRONZE.game_logs'
        query = 'INSERT INTO %s(%s) VALUES %%s ON CONFLICT (TEAM_ID, GAME_ID) DO NOTHING' % (table, columns) # upsert the data
        cursor = conn.cursor()
        try:
            print('This is the query:', query)
            print('These are the columns:', columns)
            execute_values(cursor, query, rows)
            conn.commit()
            print(f'Inserted {df.shape[0]} rows')
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
        cursor.close()

    data = api_get_game_logs()
    postgres_insert_data(data)

workflow()