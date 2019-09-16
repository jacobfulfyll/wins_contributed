import psycopg2 as pg2
import pandas as pd

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

all_time_wins = """SELECT player_name,
                    SUM( ROUND( wins_contr::numeric, 3) ) WINS
                            FROM(
                                SELECT *
                                FROM reg_season_2013_14
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2014_15
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2015_16
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2016_17
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2017_18
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2018_19) t
                WHERE t.team_id = 1610612752
                AND t.win_loss = 1
                GROUP BY t.player_id, t.player_name
                ORDER BY WINS DESC
                LIMIT 10;"""

all_time_wins_df = pd.read_sql(all_time_wins, con=conn)
conn.close()

print(all_time_wins_df)

teams = [1610612737,
               1610612738,
               1610612751,
               1610612766,
               1610612741,
               1610612739,
               1610612742,
               1610612743,
               1610612765,
               1610612744,
               1610612745,
               1610612754,
               1610612746,
               1610612747,
               1610612763,
               1610612748,
               1610612749,
               1610612750,
               1610612740,
               1610612752,
               1610612760,
               1610612753,
               1610612755,
               1610612756,
               1610612757,
               1610612758,
               1610612759,
               1610612761,
               1610612762,
               1610612764,]
'''
discrepancy_df = pd.DataFrame()
for team in teams:
    team_df = wins_df[wins_df['team_id'] == team]
    team_df = team_df.sort_values(by='wins', ascending=False)
    team_df['discrepancy'] = 0
    team_df = team_df.reset_index()
    print(team_df)
    for idx, player in team_df.iterrows():
        
        if player['wins'] == 0 or idx + 1 == len(team_df):
            print('im here')
            break
        else:
            discrepancy = player['wins'] - team_df.loc[[idx + 1]]['wins']
            team_df.loc[[idx], ['discrepancy']] = discrepancy[idx + 1]
    print(team_df)
    discrepancy_df = discrepancy_df.append(team_df)

print(discrepancy_df.reset_index().drop(columns=['level_0', 'index']).sort_values(by='discrepancy', ascending=False))
'''