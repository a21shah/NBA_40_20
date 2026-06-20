import datetime
from airflow.sdk import dag, task, get_current_context
from nba_api.stats.endpoints import teamyearbyyearstats
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from time import sleep

@dag(
    dag_id="nba_team_season_stats",
    schedule=None,
    start_date=datetime.datetime(2026, 3, 17),
    catchup=False,
    tags=["Season Stats"],
)
def workflow():

    conn = psycopg2.connect(
                    host='postgres',
                    port='5432',
                    dbname='nba_db',
                    user='airflow',
                    password='airflow'
                )
    cursor = conn.cursor()

    @task()
    def get_team_ids():
        table_game_logs = 'BRONZE.game_logs'

        query_team_ids = f'SELECT DISTINCT team_id FROM {table_game_logs}' # get distinct team ids

        cursor.execute(query_team_ids)
        rows = cursor.fetchall()
        team_ids = []
        for row in rows:
            team_ids.append(row)
        
        return team_ids

    @task()
    def api_get_team_stats(team_ids):
        context = get_current_context()

        cols = ['TEAM_ID', 'TEAM_CITY', 'TEAM_NAME', 'YEAR', 'GP', 'WINS', 'LOSSES', 'CONF_RANK', 'CONF_COUNT', 'PO_WINS', 'PO_LOSSES', 'NBA_FINALS_APPEARANCE']
        df_final = pd.DataFrame()
        counter = 0
        batch = 1

        team_id_override = context['dag_run'].conf.get('team_id', None)
        if team_id_override:
            team_ids = [team_id_override]
        
        for team_id in team_ids:
            print(f'Getting data for Team: {team_id}')
            
            stats = teamyearbyyearstats.TeamYearByYearStats(
                team_id = team_id,
                timeout=60
            )

            df = stats.get_data_frames()[0]
            df = df[cols]
            print(df.shape)

            counter += 1
            print(f'Batch: {batch}, Counter: {counter}')

            df_final = pd.concat([df_final, df])

            if counter < len(team_ids):
                if counter % 10 == 0:
                    sleep(120)
                    batch += 1
                else:
                    sleep(30)

        return df_final
    
    @task()
    def postgres_ingest_data(df):
        rows = list(df.itertuples(index=False, name=None))
        columns = ','.join(list(df.columns.to_list()))
        table_team_stats = 'BRONZE.team_season_stats'
        
        query = f"""INSERT INTO {table_team_stats}({columns}) VALUES %s 
                    ON CONFLICT (year, team_id) 
                    DO UPDATE SET
                    gp = EXCLUDED.gp,
                    wins = EXCLUDED.wins,
                    losses = EXCLUDED.losses,
                    conf_rank = EXCLUDED.conf_rank,
                    po_wins = EXCLUDED.po_wins,
                    po_losses = EXCLUDED.po_losses,
                    nba_finals_appearance = EXCLUDED.nba_finals_appearance
                    """ # upsert the data
        
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
        print('Connection closed')

    ids = get_team_ids()
    df = api_get_team_stats(ids)
    postgres_ingest_data(df)

workflow()