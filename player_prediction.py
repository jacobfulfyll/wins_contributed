import pandas as pd
from Stat_Calculations.yearly_stats import compile_team_yearly_stats, compile_yearly_stats, season_rankings_by_game
from Stat_Calculations.compile_data import create_stats_df
import numpy as np
import math
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
from sklearn import preprocessing
import psycopg2 as pg2
from sqlalchemy import create_engine


def weird_division(n, d):
    return n / d if d else 0

def wins_contr_projection_df():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    similar_seasons = """SELECT player_name, player_id, season_end, similar_player_1_id, similar_player_1_season_end, similar_player_2_id, similar_player_2_season_end, similar_player_3_id, similar_player_3_season_end, similar_player_4_id, similar_player_4_season_end, similar_player_5_id, similar_player_5_season_end
                    FROM nearest_neighbors"""

    
    
    
    
    similar_seasons_df = pd.read_sql(similar_seasons, con=conn)

    current_player_prior_1 = []
    current_player_prior_2= []
    current_player_prior_3 = []
    current_player_prior_4 = []
    current_player_prior_5 = []
    similar_player_1_prior_season_change = []
    similar_player_1_current_season_change = []
    similar_player_1_following_season_change = []
    similar_player_2_prior_season_change = []
    similar_player_2_current_season_change = []
    similar_player_2_following_season_change = []
    similar_player_3_prior_season_change = []
    similar_player_3_current_season_change = []
    similar_player_3_following_season_change = []
    similar_player_4_prior_season_change = []
    similar_player_4_current_season_change = []
    similar_player_4_following_season_change = []
    similar_player_5_prior_season_change = []
    similar_player_5_current_season_change = []
    similar_player_5_following_season_change = []


    player_id_list = []
    player_name_list = []
    season_end_list = []
    similar_player_prior_list = [similar_player_1_prior_season_change, similar_player_2_prior_season_change, similar_player_3_prior_season_change, similar_player_4_prior_season_change, similar_player_5_prior_season_change]
    similar_player_current_list = [similar_player_1_current_season_change, similar_player_2_current_season_change, similar_player_3_current_season_change, similar_player_4_current_season_change, similar_player_5_current_season_change]
    similar_player_following_list =  [similar_player_1_following_season_change, similar_player_2_following_season_change, similar_player_3_following_season_change, similar_player_4_following_season_change, similar_player_5_following_season_change]
    
    for idx, row in similar_seasons_df.iterrows():
        print(str(idx))

        current_player_id = row[1]
        current_season_end = row[2]
        current_season = """SELECT *
                            FROM yearly_stats_by_season
                            WHERE player_id = %(current_player_id)s
                            AND season_type = 'Regular Season'
                            AND season_end < %(current_season_end)s
                            ORDER BY season_end"""
        
        current_seasons_df = pd.read_sql(current_season, con=conn, params={'current_player_id': current_player_id, 'current_season_end':current_season_end})

        #print(current_seasons_df)
        if len(current_seasons_df) == 5:

            current_player_prior_1.append(current_seasons_df.loc[0, 'wins_contr'] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, 'wins_contr'] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, 'wins_contr'] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(current_seasons_df.loc[3, 'wins_contr'] * current_seasons_df.loc[3, 'games_played'])
            current_player_prior_5.append(current_seasons_df.loc[4, 'wins_contr'] * current_seasons_df.loc[4, 'games_played'])
            
            
        elif len(current_seasons_df) == 4:
            current_player_prior_1.append(current_seasons_df.loc[0, 'wins_contr'] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, 'wins_contr'] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, 'wins_contr'] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(current_seasons_df.loc[3, 'wins_contr'] * current_seasons_df.loc[3, 'games_played'])
            current_player_prior_5.append(0)
            
        
        elif len(current_seasons_df) == 3:
            current_player_prior_1.append(current_seasons_df.loc[0, 'wins_contr'] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, 'wins_contr'] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, 'wins_contr'] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)

        elif len(current_seasons_df) == 2:
            current_player_prior_1.append(current_seasons_df.loc[0, 'wins_contr'] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, 'wins_contr'] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)
            

        elif len(current_seasons_df) == 1:
            current_player_prior_1.append(current_seasons_df.loc[0, 'wins_contr'] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(0)
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)

        else:
            current_player_prior_1.append(0)
            current_player_prior_2.append(0)
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)
            

        for i in range(5):
            
            similar_player_id = row[3 + (i*2)]
            similar_season_end = row[4 + (i*2)]
            similar_seasons = """SELECT *
                                    FROM yearly_stats_by_season
                                    WHERE player_id = %(similar_player_id)s
                                    AND season_type = 'Regular Season'
                                    AND (season_end = %(similar_season_end)s
                                    OR season_end = %(similar_season_end)s + 1
                                    OR season_end = %(similar_season_end)s - 1)"""
        
        
            similar_seasons_df = pd.read_sql(similar_seasons, con=conn, params={'similar_player_id': similar_player_id, 'similar_season_end':similar_season_end})
            
            if len(similar_seasons_df) == 3:
                similar_player_prior_list[i].append(weird_division(similar_seasons_df.loc[0, 'wc_change'], similar_seasons_df.loc[0, 'wins_contr']) * similar_seasons_df.loc[0, 'gp_change'])
                similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[1, 'wc_change'], similar_seasons_df.loc[1, 'wins_contr']) * similar_seasons_df.loc[1, 'gp_change'])
                similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[2, 'wc_change'], similar_seasons_df.loc[2, 'wins_contr']) * similar_seasons_df.loc[2, 'gp_change'])
                
            elif len(similar_seasons_df) == 2 and similar_season_end == similar_seasons_df.loc[0, 'season_end']:
                similar_player_prior_list[i].append(0)
                similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[0, 'wc_change'], similar_seasons_df.loc[0, 'wins_contr']) * similar_seasons_df.loc[0, 'gp_change'])
                similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[1, 'wc_change'], similar_seasons_df.loc[1, 'wins_contr']) * similar_seasons_df.loc[1, 'gp_change'])
            
            elif len(similar_seasons_df) == 1:
                similar_player_prior_list[i].append(0)
                similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[0, 'wc_change'], similar_seasons_df.loc[0, 'wins_contr']) * similar_seasons_df.loc[0, 'gp_change'])
                similar_player_following_list[i].append(0)

            else:
                similar_player_prior_list[i].append(weird_division(similar_seasons_df.loc[0, 'wc_change'], similar_seasons_df.loc[0, 'wins_contr']) * similar_seasons_df.loc[0, 'gp_change'])
                similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[1, 'wc_change'], similar_seasons_df.loc[1, 'wins_contr']) * similar_seasons_df.loc[1, 'gp_change'])
                similar_player_following_list[i].append(0)
        player_id_list.append(row[1])
        player_name_list.append(row[0])
        season_end_list.append(row[2])  
    
    

    projection_df = pd.DataFrame()
    projection_df['player_id'] = player_id_list
    projection_df['player_name'] = player_name_list
    projection_df['season_end'] = season_end_list
    projection_df['cp_prior_1'] = current_player_prior_1
    projection_df['cp_prior_2'] = current_player_prior_2
    projection_df['cp_prior_3'] = current_player_prior_3
    projection_df['cp_prior_4'] = current_player_prior_4
    projection_df['cp_prior_5'] = current_player_prior_5
    projection_df['sp1_prior_season'] = similar_player_1_prior_season_change
    projection_df['sp1_current_season'] = similar_player_1_current_season_change
    projection_df['sp1_following_season'] = similar_player_1_following_season_change
    projection_df['sp2_prior_season'] = similar_player_2_prior_season_change
    projection_df['sp2_current_season'] = similar_player_2_current_season_change
    projection_df['sp2_following_season'] = similar_player_2_following_season_change
    projection_df['sp3_prior_season'] = similar_player_3_prior_season_change
    projection_df['sp3_current_season'] = similar_player_3_current_season_change
    projection_df['sp3_following_season'] = similar_player_3_following_season_change
    projection_df['sp4_prior_season'] = similar_player_4_prior_season_change
    projection_df['sp4_current_season'] = similar_player_4_current_season_change
    projection_df['sp4_following_season'] = similar_player_4_following_season_change
    projection_df['sp5_prior_season'] = similar_player_5_prior_season_change
    projection_df['sp5_current_season'] = similar_player_5_current_season_change
    projection_df['sp5_following_season'] = similar_player_5_following_season_change
    
    
    '''reg_seasons = """SELECT DISTINCT player_id, reg_seasons_played
                    FROM all_time_stats"""

    reg_seasons_df = pd.read_sql(reg_seasons, con=conn)

    projection_df = pd.merge(projection_df, reg_seasons_df, on='player_id')'''

    wins_contributed = """SELECT player_id, season_end, wins_contr
                                FROM yearly_stats_by_season
                                WHERE season_type = 'Regular Season'
                                """

    wins_contributed_df = pd.read_sql(wins_contributed, con=conn)

    merged_df = pd.merge(projection_df, wins_contributed_df, on=['player_id', 'season_end'])
    print(merged_df)
    wins_contributed_df = merged_df[['player_id', 'season_end', 'wins_contr']]
    projection_df = merged_df.drop(columns=['wins_contr'])

    #wins_contributed_df['uniq_check'] = [str(row[1]) + str(row[0]) for idx, row in wins_contributed_df.iterrows()]
    #projection_df['uniq_check'] = [str(row[0]) + str(row[2]) for idx, row in projection_df.iterrows()]

    print(wins_contributed_df)
    print(projection_df)

    # unique_ids = []
    # for idx, p in projection_df['uniq_check'].iteritems():
    #     #print(p)
    #     if p in wins_contributed_df['uniq_check'].tolist():
    #         pass
    #     else:
    #         unique_ids.append(p)

    # for current_id in unique_ids:
    #     #print(current_id)
    #     wins_contributed_df = wins_contributed_df[wins_contributed_df['uniq_check'] != current_id]
    
    # wins_contributed_df = wins_contributed_df.drop(columns='uniq_check')
    # projection_df = projection_df.drop(columns='uniq_check')

    y = wins_contributed_df.sort_values(by=['player_id', 'season_end'])
    X = projection_df.sort_values(by=['player_id', 'season_end'])

    y = y.drop(columns=['player_id', 'season_end'])
    print(X)
    print(y)
    conn.close()

    sql_table_1 = 'wc_projection_data'
    sql_table_2 = 'wc_actual_results'
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    X.to_sql(sql_table_1, con = engine, if_exists='replace', index=False)
    y.to_sql(sql_table_2, con = engine, if_exists='replace', index=False)
    conn.close()

#wins_contr_projection_df()


def wins_contr_more_detailed_projection_df(win_loss):
    if win_loss == 1:
        change = 'wc_change'
        stat = 'wins_contr'
        sql_table_1 = 'wc_more_detailed_projection_data'
        sql_table_2 = 'wc_actual_results'
    else:
        change = 'wc_il_change'
        stat = 'wins_contr_in_loss' 
        sql_table_1 = 'wc_il_more_detailed_projection_data'
        sql_table_2 = 'wc_il_actual_results' 

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    similar_seasons = """SELECT player_name, player_id, season_end, similar_player_1_id, similar_player_1_season_end, similar_player_2_id, similar_player_2_season_end, similar_player_3_id, similar_player_3_season_end, similar_player_4_id, similar_player_4_season_end, similar_player_5_id, similar_player_5_season_end
                    FROM nearest_neighbors"""

    
    
    
    
    similar_seasons_df = pd.read_sql(similar_seasons, con=conn)

    current_player_prior_1 = []
    current_player_prior_2= []
    current_player_prior_3 = []
    current_player_prior_4 = []
    current_player_prior_5 = []
    similar_player_1_prior_1 = []
    similar_player_1_prior_2 = []
    similar_player_1_prior_3 = []
    similar_player_1_prior_4 = []
    similar_player_1_prior_5 = []
    similar_player_1_current = []
    similar_player_1_following = []
    similar_player_2_prior_1 = []
    similar_player_2_prior_2 = []
    similar_player_2_prior_3 = []
    similar_player_2_prior_4 = []
    similar_player_2_prior_5 = []
    similar_player_2_current = []
    similar_player_2_following = []
    similar_player_3_prior_1 = []
    similar_player_3_prior_2 = []
    similar_player_3_prior_3 = []
    similar_player_3_prior_4 = []
    similar_player_3_prior_5 = []
    similar_player_3_current = []
    similar_player_3_following = []
    similar_player_4_prior_1 = []
    similar_player_4_prior_2 = []
    similar_player_4_prior_3 = []
    similar_player_4_prior_4 = []
    similar_player_4_prior_5 = []
    similar_player_4_current = []
    similar_player_4_following = []
    similar_player_5_prior_1 = []
    similar_player_5_prior_2 = []
    similar_player_5_prior_3 = []
    similar_player_5_prior_4 = []
    similar_player_5_prior_5 = []
    similar_player_5_current = []
    similar_player_5_following = []


    player_id_list = []
    player_name_list = []
    season_end_list = []
    similar_player_prior_1_list = [similar_player_1_prior_1, similar_player_2_prior_1, similar_player_3_prior_1, similar_player_4_prior_1, similar_player_5_prior_1]
    similar_player_prior_2_list = [similar_player_1_prior_2, similar_player_2_prior_2, similar_player_3_prior_2, similar_player_4_prior_2, similar_player_5_prior_2]
    similar_player_prior_3_list = [similar_player_1_prior_3, similar_player_2_prior_3, similar_player_3_prior_3, similar_player_4_prior_3, similar_player_5_prior_3]
    similar_player_prior_4_list = [similar_player_1_prior_4, similar_player_2_prior_4, similar_player_3_prior_4, similar_player_4_prior_4, similar_player_5_prior_4]
    similar_player_prior_5_list = [similar_player_1_prior_5, similar_player_2_prior_5, similar_player_3_prior_5, similar_player_4_prior_5, similar_player_5_prior_5]
    similar_player_current_list = [similar_player_1_current, similar_player_2_current, similar_player_3_current, similar_player_4_current, similar_player_5_current]
    similar_player_following_list =  [similar_player_1_following, similar_player_2_following, similar_player_3_following, similar_player_4_following, similar_player_5_following]
    
    for idx, row in similar_seasons_df.iterrows():
        print(str(idx))

        current_player_id = row[1]
        current_season_end = row[2]
        current_season = """SELECT *
                            FROM yearly_stats_by_season
                            WHERE player_id = %(current_player_id)s
                            AND season_type = 'Regular Season'
                            AND season_end < %(current_season_end)s
                            ORDER BY season_end"""
        
        current_seasons_df = pd.read_sql(current_season, con=conn, params={'current_player_id': current_player_id, 'current_season_end':current_season_end})

        #print(current_seasons_df)
        if len(current_seasons_df) == 5:
            
            current_player_prior_1.append(current_seasons_df.loc[0, stat] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, stat] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, stat] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(current_seasons_df.loc[3, stat] * current_seasons_df.loc[3, 'games_played'])
            current_player_prior_5.append(current_seasons_df.loc[4, stat] * current_seasons_df.loc[4, 'games_played'])
            
            
        elif len(current_seasons_df) == 4:
            current_player_prior_1.append(current_seasons_df.loc[0, stat] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, stat] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, stat] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(current_seasons_df.loc[3, stat] * current_seasons_df.loc[3, 'games_played'])
            current_player_prior_5.append(0)
            
        
        elif len(current_seasons_df) == 3:
            current_player_prior_1.append(current_seasons_df.loc[0, stat] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, stat] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(current_seasons_df.loc[2, stat] * current_seasons_df.loc[2, 'games_played'])
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)

        elif len(current_seasons_df) == 2:
            current_player_prior_1.append(current_seasons_df.loc[0, stat] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(current_seasons_df.loc[1, stat] * current_seasons_df.loc[1, 'games_played'])
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)
            

        elif len(current_seasons_df) == 1:
            current_player_prior_1.append(current_seasons_df.loc[0, stat] * current_seasons_df.loc[0, 'games_played'])
            current_player_prior_2.append(0)
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)

        else:
            current_player_prior_1.append(0)
            current_player_prior_2.append(0)
            current_player_prior_3.append(0)
            current_player_prior_4.append(0)
            current_player_prior_5.append(0)
            

        for i in range(5):
            
            similar_player_id = row[3 + (i*2)]
            similar_season_end = row[4 + (i*2)]
            similar_seasons = """SELECT *
                                    FROM yearly_stats_by_season
                                    WHERE player_id = %(similar_player_id)s
                                    AND season_type = 'Regular Season'
                                    AND season_end <= %(similar_season_end)s + 1"""
        
        
            similar_seasons_df = pd.read_sql(similar_seasons, con=conn, params={'similar_player_id': similar_player_id, 'similar_season_end':similar_season_end})
            
            if len(similar_seasons_df) == 6:
                if similar_seasons_df.loc[5, 'season_end'] == 2019:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[4, change], similar_seasons_df.loc[4, stat]) * similar_seasons_df.loc[4, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
                    similar_player_prior_3_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_prior_4_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_5_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[5, change], similar_seasons_df.loc[5, stat]) * similar_seasons_df.loc[5, 'gp_change'])
                    similar_player_following_list[i].append(0)
                else:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_prior_3_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_4_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[4, change], similar_seasons_df.loc[4, stat]) * similar_seasons_df.loc[4, 'gp_change'])
                    similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[5, change], similar_seasons_df.loc[5, stat]) * similar_seasons_df.loc[5, 'gp_change'])

            elif len(similar_seasons_df) == 5:
                if similar_seasons_df.loc[4, 'season_end'] == 2019:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_prior_3_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_4_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[4, change], similar_seasons_df.loc[4, stat]) * similar_seasons_df.loc[4, 'gp_change'])
                    similar_player_following_list[i].append(0)
                else:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_3_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
                    similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[4, change], similar_seasons_df.loc[4, stat]) * similar_seasons_df.loc[4, 'gp_change'])

            elif len(similar_seasons_df) == 4:
                if similar_seasons_df.loc[3, 'season_end'] == 2019:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_3_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
                    similar_player_following_list[i].append(0)
                else:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_3_list[i].append(0)
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[3, change], similar_seasons_df.loc[3, stat]) * similar_seasons_df.loc[3, 'gp_change'])
            
            elif len(similar_seasons_df) == 3:
                if similar_seasons_df.loc[2, 'season_end'] == 2019:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_prior_2_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_3_list[i].append(0)
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])
                    similar_player_following_list[i].append(0)
                else:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_2_list[i].append(0)
                    similar_player_prior_3_list[i].append(0)
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[2, change], similar_seasons_df.loc[2, stat]) * similar_seasons_df.loc[2, 'gp_change'])

            elif len(similar_seasons_df) == 2:
                if similar_seasons_df.loc[1, 'season_end'] == 2019:
                    similar_player_prior_1_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_prior_2_list[i].append(0)
                    similar_player_prior_3_list[i].append(0)
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])
                    similar_player_following_list[i].append(0)
                else:
                    similar_player_prior_1_list[i].append(0)
                    similar_player_prior_2_list[i].append(0)
                    similar_player_prior_3_list[i].append(0)
                    similar_player_prior_4_list[i].append(0)
                    similar_player_prior_5_list[i].append(0)
                    similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                    similar_player_following_list[i].append(weird_division(similar_seasons_df.loc[1, change], similar_seasons_df.loc[1, stat]) * similar_seasons_df.loc[1, 'gp_change'])

            else:
                similar_player_prior_1_list[i].append(0)
                similar_player_prior_2_list[i].append(0)
                similar_player_prior_3_list[i].append(0)
                similar_player_prior_4_list[i].append(0)
                similar_player_prior_5_list[i].append(0)
                similar_player_current_list[i].append(weird_division(similar_seasons_df.loc[0, change], similar_seasons_df.loc[0, stat]) * similar_seasons_df.loc[0, 'gp_change'])
                similar_player_following_list[i].append(0)

        player_id_list.append(row[1])
        player_name_list.append(row[0])
        season_end_list.append(row[2])  
    
    

    projection_df = pd.DataFrame()
    projection_df['player_id'] = player_id_list
    projection_df['player_name'] = player_name_list
    projection_df['season_end'] = season_end_list
    projection_df['cp_prior_1'] = current_player_prior_1
    projection_df['cp_prior_2'] = current_player_prior_2
    projection_df['cp_prior_3'] = current_player_prior_3
    projection_df['cp_prior_4'] = current_player_prior_4
    projection_df['cp_prior_5'] = current_player_prior_5
    projection_df['sp1_prior_1'] = similar_player_1_prior_1
    projection_df['sp1_prior_2'] = similar_player_1_prior_2
    projection_df['sp1_prior_3'] = similar_player_1_prior_3
    projection_df['sp1_prior_4'] = similar_player_1_prior_4
    projection_df['sp1_prior_5'] = similar_player_1_prior_5
    projection_df['sp1_current'] = similar_player_1_current
    projection_df['sp1_following'] = similar_player_1_following
    projection_df['sp2_prior_1'] = similar_player_2_prior_1
    projection_df['sp2_prior_2'] = similar_player_2_prior_2
    projection_df['sp2_prior_3'] = similar_player_2_prior_3
    projection_df['sp2_prior_4'] = similar_player_2_prior_4
    projection_df['sp2_prior_5'] = similar_player_2_prior_5
    projection_df['sp2_current'] = similar_player_2_current
    projection_df['sp2_following'] = similar_player_2_following
    projection_df['sp3_prior_1'] = similar_player_3_prior_1
    projection_df['sp3_prior_2'] = similar_player_3_prior_2
    projection_df['sp3_prior_3'] = similar_player_3_prior_3
    projection_df['sp3_prior_4'] = similar_player_3_prior_4
    projection_df['sp3_prior_5'] = similar_player_3_prior_5
    projection_df['sp3_current'] = similar_player_3_current
    projection_df['sp3_following'] = similar_player_3_following
    projection_df['sp4_prior_1'] = similar_player_4_prior_1
    projection_df['sp4_prior_2'] = similar_player_4_prior_2
    projection_df['sp4_prior_3'] = similar_player_4_prior_3
    projection_df['sp4_prior_4'] = similar_player_4_prior_4
    projection_df['sp4_prior_5'] = similar_player_4_prior_5
    projection_df['sp4_current'] = similar_player_4_current
    projection_df['sp4_following'] = similar_player_4_following
    projection_df['sp5_prior_1'] = similar_player_5_prior_1
    projection_df['sp5_prior_2'] = similar_player_5_prior_2
    projection_df['sp5_prior_3'] = similar_player_5_prior_3
    projection_df['sp5_prior_4'] = similar_player_5_prior_4
    projection_df['sp5_prior_5'] = similar_player_5_prior_5
    projection_df['sp5_current'] = similar_player_5_current
    projection_df['sp5_following'] = similar_player_5_following
    
    
    '''reg_seasons = """SELECT DISTINCT player_id, reg_seasons_played
                    FROM all_time_stats"""

    reg_seasons_df = pd.read_sql(reg_seasons, con=conn)

    projection_df = pd.merge(projection_df, reg_seasons_df, on='player_id')'''

    if win_loss == 1:
        wins_contributed = """SELECT player_id, season_end, wins_contr
                                    FROM yearly_stats_by_season
                                    WHERE season_type = 'Regular Season'
                                    """
    else:
        wins_contributed = """SELECT player_id, season_end, wins_contr_in_loss
                            FROM yearly_stats_by_season
                            WHERE season_type = 'Regular Season'
                            """

    wins_contributed_df = pd.read_sql(wins_contributed, con=conn)
    print(wins_contributed_df.columns)
    print(projection_df.columns)
    merged_df = pd.merge(projection_df, wins_contributed_df, on=['player_id', 'season_end'])
    #print(merged_df)
    wins_contributed_df = merged_df[['player_id', 'season_end', stat]]
    projection_df = merged_df.drop(columns=[stat])

    # print(wins_contributed_df)
    # print(projection_df)

    y = wins_contributed_df.sort_values(by=['player_id', 'season_end'])
    X = projection_df.sort_values(by=['player_id', 'season_end'])

    y = y.drop(columns=['player_id', 'season_end'])

    conn.close()
    
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    X.to_sql(sql_table_1, con = engine, if_exists='replace', index=False)
    y.to_sql(sql_table_2, con = engine, if_exists='replace', index=False)
    conn.close()

#wins_contr_more_detailed_projection_df(win_loss=0)

def grid_search(X, y):

    params = {'min_samples_leaf': 2, 'max_depth':6, 'subsample':.6, 'n_estimators':1500, 'min_samples_split':10, 'loss': 'ls', 'learning_rate': .01, 'subsample': .6}
    clf = ensemble.GradientBoostingRegressor(**params)
    
    #Choose all predictors except target & IDcols
    param_test1 = {}
    gsearch1 = GridSearchCV(estimator = clf, 
    param_grid = param_test1, scoring='neg_mean_squared_error',n_jobs=-1,iid=False, cv=5)
    gsearch1.fit(X,np.ravel(y))

    print('Best Estimator: ')
    print(gsearch1.best_estimator_)
    print()
    print()
    print('Best Params: ')
    print(gsearch1.best_params_)
    print()
    print()
    print('Best Score: ')
    print(gsearch1.best_score_)


def player_projections():
    
    avg_predictions_df = pd.DataFrame()
    
    for i in range(10):
        conn = pg2.connect(dbname= "wins_contr", host = "localhost")
        cur = conn.cursor()

        X_query_wins = """SELECT *
                FROM wc_more_detailed_projection_data"""
        
        X_query_losses = """SELECT *
                FROM wc_il_more_detailed_projection_data"""


        y_query_wins = """SELECT *
                FROM wc_actual_results"""

        y_query_losses = """SELECT *
                FROM wc_il_actual_results"""

        
        X_wins= pd.read_sql(X_query_wins, con=conn)
        X_losses= pd.read_sql(X_query_losses, con=conn)
        y_wins = pd.read_sql(y_query_wins, con=conn)
        y_losses = pd.read_sql(y_query_losses, con=conn)

        y_wins = np.ravel(y_wins)
        y_losses = np.ravel(y_losses)

        X_wins= X_wins.drop(columns='player_name')
        X_losses= X_losses.drop(columns='player_name')

        X_train_wins, X_test_wins, y_train_wins, y_test_wins = train_test_split(X_wins, y_wins, test_size=0.25, random_state=42)
        X_train_losses, X_test_losses, y_train_losses, y_test_losses = train_test_split(X_losses, y_losses, test_size=0.25, random_state=42)

        params = {'min_samples_leaf': 2, 'max_depth':6, 'subsample':.6, 'n_estimators':1500, 'min_samples_split':10, 'loss': 'ls', 'learning_rate': .01, 'subsample': .6}
        wins_model = ensemble.GradientBoostingRegressor(**params)
        losses_model = ensemble.GradientBoostingRegressor(**params)

        wins_model.fit(X_train_wins, y_train_wins)
        losses_model.fit(X_train_losses, y_train_losses)

        wins_mse = mean_squared_error(y_test_wins, wins_model.predict(X_test_wins))
        wins_rmse = np.sqrt(wins_mse)

        losses_mse = mean_squared_error(y_test_losses, losses_model.predict(X_test_losses))
        losses_rmse = np.sqrt(losses_mse)

        print("wins_RMSE: %.4f" % wins_rmse)
        print("losses_RMSE: %.4f" % losses_rmse)

        wins_predictions_2020 = """SELECT *
                                FROM wc_more_detailed_projection_data
                                WHERE season_end = 2019"""

        losses_predictions_2020 = """SELECT *
                            FROM wc_il_more_detailed_projection_data
                            WHERE season_end = 2019"""


        
        wins_predictions_df = pd.read_sql(wins_predictions_2020, con=conn)
        losses_predictions_df = pd.read_sql(losses_predictions_2020, con=conn)
        wins_name_series = wins_predictions_df['player_name']
        losses_name_series = losses_predictions_df['player_name']

        wins_predictions_df = wins_predictions_df.drop(columns='player_name')
        wins_ynew = wins_model.predict(wins_predictions_df)

        losses_predictions_df = losses_predictions_df.drop(columns='player_name')
        losses_ynew = losses_model.predict(losses_predictions_df)

        wins_predictions_df['wins_contr'] = wins_ynew
        wins_predictions_df['player_name'] = wins_name_series

        losses_predictions_df['wins_contr_in_loss'] = losses_ynew
        losses_predictions_df['player_name'] = losses_name_series

        wins_predictions_df = wins_predictions_df[['player_id', 'player_name', 'wins_contr']]
        losses_predictions_df = losses_predictions_df[['player_id', 'player_name', 'wins_contr_in_loss']]

        predictions_df = pd.merge(wins_predictions_df, losses_predictions_df, on=['player_id', 'player_name'])

        avg_predictions_df = avg_predictions_df.append(predictions_df)

        conn.close()
    print(avg_predictions_df)
    final_prediction_df = avg_predictions_df.groupby(['player_id', 'player_name'], as_index=False)
    final_prediction_df = final_prediction_df.aggregate(np.mean)
    print(final_prediction_df)

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    final_prediction_df.to_sql('player_projections_2020', con = engine, if_exists='replace', index=False)
    conn.close()

player_projections()
'''
# #############################################################################
# Plot training deviance

# compute test set deviance
    test_score = np.zeros((params['n_estimators'],), dtype=np.float64)

    for i, y_pred in enumerate(clf.staged_predict(X_test)):
        test_score[i] = clf.loss_(y_test, y_pred)

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title('Deviance')
    plt.plot(np.arange(params['n_estimators']) + 1, clf.train_score_, 'b-',
            label='Training Set Deviance')
    plt.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
            label='Test Set Deviance')
    plt.legend(loc='upper right')
    plt.xlabel('Boosting Iterations')
    plt.ylabel('Deviance')

# #############################################################################
# Plot feature importance
    feature_importance = clf.feature_importances_
    # make importances relative to max importance
    feature_importance = 100.0 * (feature_importance / feature_importance.max())
    sorted_idx = np.argsort(feature_importance)
    pos = np.arange(sorted_idx.shape[0]) + .5
    plt.subplot(1, 2, 2)
    plt.barh(pos, feature_importance[sorted_idx], align='center')
    plt.yticks(pos, X.feature_names[sorted_idx])
    plt.xlabel('Relative Importance')
    plt.title('Variable Importance')
    plt.show()
'''
