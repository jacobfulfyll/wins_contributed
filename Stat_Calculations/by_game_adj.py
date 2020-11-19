import pandas as pd
from compile_data import create_stats_df
import numpy as np
import psycopg2 as pg2
from sqlalchemy import create_engine

master_df = create_stats_df()



def depth_chart_position_by_game_splits():
    yearly_df = master_df[master_df['jacob_value'] != 0][['season_type', 'season_end', 'game_id', 'win_loss','team_id', 'player_id', 'player_name', 'wins_contr']]    
    
    yearly_df['wc_rank_team'] = 0
    yearly_df['wc_depth_chart_diff'] = 0
    yearly_df = yearly_df.sort_values(['game_id', 'team_id', 'wins_contr'], ascending=False)
    yearly_df = yearly_df.reset_index(drop=True)
    counter = 1
    print(yearly_df)
    for idx, row in yearly_df.iterrows():
        print(str(idx) + '/' + str(len(yearly_df)))
        if idx == 0:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr'] 
        
        elif idx == len(yearly_df) - 1:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = 0

        elif yearly_df.loc[idx - 1, 'season_end'] == yearly_df.loc[idx, 'season_end'] and yearly_df.loc[idx - 1, 'season_type'] == yearly_df.loc[idx, 'season_type'] and yearly_df.loc[idx - 1, 'game_id'] == yearly_df.loc[idx, 'game_id'] and yearly_df.loc[idx - 1, 'team_id'] == yearly_df.loc[idx, 'team_id']:
            
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']
        
        else:
            counter = 1
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx - 1, 'wc_depth_chart_diff'] = 0
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']

    print(yearly_df)
    yearly_df = yearly_df.reset_index(drop=True)
    sql_table = 'all_games_ranked'
    
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    yearly_df.to_sql(sql_table, con = engine, if_exists= "replace")
    conn.close()

depth_chart_position_by_game_splits()