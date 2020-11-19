import psycopg2 as pg2
import pandas as pd
from sqlalchemy import create_engine

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

all_seasons_d_d = """CREATE TABLE all_seasons_discrepancy_depth (id SERIAL PRIMARY KEY,
                                        game_id VARCHAR(50) NOT NULL,
                                        win_loss INT NOT NULL,
                                        team_id BIGINT NOT NULL,
                                        player_id BIGINT NOT NULL,
                                        player_name VARCHAR(50) NOT NULL,
                                        season_type VARCHAR(20) NOT NULL,
                                        season_end INTEGER NOT NULL,
                                        discrepancy_total REAL NOT NULL,
                                        depth_chart_rank INTEGER NOT NULL);
                                   """
             
cur.execute(all_seasons_d_d)
conn.commit()

discrepancy_depth_rank_query = """SELECT game_id, win_loss, team_id, player_id, player_name, season_end, season_type, value_contributed
                                    FROM all_seasons_value_contributed
                                    ORDER BY game_id, team_id, value_contributed DESC;"""


discrepancy_depth_rank_df = pd.read_sql(discrepancy_depth_rank_query, con=conn)

conn.close()


team_id = 0
depth_chart_rank = 1
depth_chart_rank_list = []
discrepancy_list = []

for idx in range(len(discrepancy_depth_rank_df)):
    if idx + 1 == len(discrepancy_depth_rank_df):
        team_id = discrepancy_depth_rank_df.loc[idx, 'team_id']

        discrepancy = 0
        discrepancy_list.append(discrepancy)

        if discrepancy_depth_rank_df.loc[idx, 'value_contributed'] == discrepancy_depth_rank_df.loc[idx - 1, 'value_contributed']:
            depth_chart_rank -= 1
            depth_chart_rank_list.append(depth_chart_rank)
        else:
            depth_chart_rank_list.append(depth_chart_rank)
    
    elif idx == 0:
        team_id = discrepancy_depth_rank_df.loc[idx, 'team_id']
        depth_chart_rank_list.append(depth_chart_rank)
        discrepancy = discrepancy_depth_rank_df.loc[idx, 'value_contributed'] - discrepancy_depth_rank_df.loc[idx + 1, 'value_contributed'] 
        discrepancy_list.append(discrepancy)

        depth_chart_rank += 1

    elif discrepancy_depth_rank_df.loc[idx, 'team_id'] != team_id:
        team_id = discrepancy_depth_rank_df.loc[idx, 'team_id']
        depth_chart_rank = 1
        discrepancy = discrepancy_depth_rank_df.loc[idx, 'value_contributed'] - discrepancy_depth_rank_df.loc[idx + 1, 'value_contributed']
        discrepancy_list.append(discrepancy)

        if discrepancy_depth_rank_df.loc[idx, 'value_contributed'] == discrepancy_depth_rank_df.loc[idx - 1, 'value_contributed']:
            depth_chart_rank -= 1
            depth_chart_rank_list.append(depth_chart_rank)
        else:
            depth_chart_rank_list.append(depth_chart_rank)
        
        
        depth_chart_rank += 1
    
    elif discrepancy_depth_rank_df.loc[idx + 1, 'team_id'] != team_id:
        team_id = discrepancy_depth_rank_df.loc[idx, 'team_id']
        discrepancy = 0
        discrepancy_list.append(discrepancy)

        if discrepancy_depth_rank_df.loc[idx, 'value_contributed'] == discrepancy_depth_rank_df.loc[idx - 1, 'value_contributed']:
            depth_chart_rank -= 1
            depth_chart_rank_list.append(depth_chart_rank)
        else:
            depth_chart_rank_list.append(depth_chart_rank)
        
    
    else:
        team_id = discrepancy_depth_rank_df.loc[idx, 'team_id']
        discrepancy = discrepancy_depth_rank_df.loc[idx, 'value_contributed'] - discrepancy_depth_rank_df.loc[idx + 1, 'value_contributed']
        discrepancy_list.append(discrepancy)

        if discrepancy_depth_rank_df.loc[idx, 'value_contributed'] == discrepancy_depth_rank_df.loc[idx - 1, 'value_contributed']:
            depth_chart_rank -= 1
            depth_chart_rank_list.append(depth_chart_rank)
        else:
            depth_chart_rank_list.append(depth_chart_rank)
        

        depth_chart_rank += 1

discrepancy_depth_rank_df['depth_chart_rank'] = depth_chart_rank_list
discrepancy_depth_rank_df['discrepancy_total'] = discrepancy_list
print(discrepancy_depth_rank_df)
discrepancy_depth_rank_df = discrepancy_depth_rank_df.drop(columns='value_contributed')

conn = pg2.connect(dbname = 'postgres', host = "localhost")
conn.autocommit = True
engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
discrepancy_depth_rank_df.to_sql('all_seasons_discrepancy_depth', con = engine, if_exists= "append", index=False)
conn.close()