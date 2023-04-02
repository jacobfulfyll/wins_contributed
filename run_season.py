import sys
import pandas as pd
import numpy as np
import psycopg2 as pg2
from sqlalchemy import create_engine
from time import sleep
from Prep_Functions.value_contr_inputs import get_value_contributed_inputs
from Prep_Functions.find_teams import get_team_info
from Prep_Functions.play_by_play import get_play_by_play_df
from run_game import get_value_contributed_boxscore
from nba_api.stats.endpoints import commonplayoffseries


def compile_all(game_id, season, season_type, season_end_year, sql_upload):
    #Create df
    #all_games_df = pd.DataFrame(columns=['game_id', 'team_id', 'opponent_id', 'player_id','player_name','points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr'])
    counter = 0
    current_game_id = int(game_id) + counter
    str_game_id = '00' + str(current_game_id)

    # Call Helper Functions
    losing_team, winning_team, home_away = get_team_info(str_game_id, season, season_type)
    val_contr_inputs_df_list = get_value_contributed_inputs(str_game_id, winning_team, losing_team, season_type, season_end_year=season_end_year, sql_upload=sql_upload)
    print(val_contr_inputs_df_list)
    play_by_play_df = get_play_by_play_df(str_game_id, home_away, season_type, season_end_year=season_end_year, sql_upload=sql_upload)
    #print(play_by_play_df.columns)
    value_contributed_boxscore, play_by_play_adjustments_df = get_value_contributed_boxscore(str_game_id, play_by_play_df, val_contr_inputs_df_list, winning_team, losing_team)
    #print(value_contributed_boxscore) 
    #print(play_by_play_adjustments_df)
    # ?????? Why don't I just return value contributed df as is, why limit columns ????????
    return value_contributed_boxscore, play_by_play_adjustments_df 

    # if season_type == 'Playoffs':
        

    #     # Call Helper Functions
    #     losing_team, winning_team, home_away = team_info(str_game_id, season, season_type)
    #     general_dfs = general_df_func(str_game_id, winning_team, losing_team, season_type, season_end_year=season_end_year)
    #     #print(general_df)
    #     game_df = game_df_func(str_game_id, home_away, season_type, season_end_year=season_end_year)
    #     #print(game_df)
    #     jacob_game_stat_df = get_value_contributed_boxscore(str_game_id, game_df, general_dfs, winning_team, winning_team, losing_team)
    #     return jacob_game_stat_df[['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id', 'player_name', 'points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr']]

    # else:

    #     # # Run until all games passed in have been run
    #     # while current_game_id <= game_id_end:
    #         # current_game_id = game_id_start + counter
    #         # str_game_id = '00' + str(current_game_id)

    #     # Call Helper Functions
    #     losing_team, winning_team, home_away = team_info(str_game_id, season, season_type)
    #     general_dfs = general_df_func(str_game_id, winning_team, losing_team, season_type, season_end_year=season_end_year)
    #     #print(general_df)
    #     game_df = game_df_func(str_game_id, home_away, season_type, season_end_year=season_end_year)
    #     #print(game_df)
    #     jacob_game_stat_df = get_value_contributed_boxscore(str_game_id, game_df, general_dfs, winning_team, winning_team, losing_team)
    #     # Append current game to previous game to create one df
    #     all_games_df = all_games_df.append(jacob_game_stat_df)

    #     counter += 1
    #     all_games_df = all_games_df.reset_index()
    #     all_games_df = all_games_df.drop(columns='index')

    #     return all_games_df[['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id', 'player_name', 'points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr']]


def run_season(season, start_game, end_game, season_type, sql_upload='no', playoff_games_list='n'):
    season_end_year = int(season[:4]) + 1

    if season_type == 'Playoffs':
        if playoff_games_list != 'n':
            playoff_game_ids = playoff_games_list
        else:
            playoff_games = commonplayoffseries.CommonPlayoffSeries(season=season)
            playoff_game_ids = playoff_games.playoff_series.get_data_frame()['GAME_ID'].tolist()

        sql_table_1 = 'value_contributed_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        sql_table_2 = 'possessional_adjustments_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        print(playoff_game_ids)

        for game_id in playoff_game_ids:
            value_contributed_boxscore, play_by_play_adjustments_df = compile_all(game_id, season, season_type, season_end_year, sql_upload)
            value_contributed_boxscore['Season_Type'] = 'Playoffs'
            play_by_play_adjustments_df['Season_Type'] = 'Playoffs'
            print(value_contributed_boxscore)
            # print(value_contributed_boxscore.iloc[:, :10])
            # print(value_contributed_boxscore.iloc[:, 10:])
            # print(value_contributed_boxscore.iloc[:, 20:])
            # print(value_contributed_boxscore.iloc[:, 30:])

            if sql_upload == 'yes' or sql_upload == 'y' or sql_upload == 'Yes':
                columns_1 = [x.lower() for x in value_contributed_boxscore.columns]
                columns_1 = [x if x != 'to' else 'tos' for x in columns_1]
                copy_1_df = value_contributed_boxscore.copy()
                copy_1_df.columns = columns_1
                
                columns_2 = [x.lower() for x in play_by_play_adjustments_df.columns]
                columns_2 = [x if x != 'to' else 'tos' for x in columns_2]
                copy_2_df = play_by_play_adjustments_df.copy()
                copy_2_df.columns = columns_2

                conn = pg2.connect(dbname = 'postgres', host = "localhost")
                conn.autocommit = True
                engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
                copy_1_df.to_sql(sql_table_1, con = engine, if_exists= "append", index=False)
                copy_2_df.to_sql(sql_table_2, con = engine, if_exists= "append", index=False)
                conn.close()
            else:
                pass

    else:
        game_id = '00' + season[:4].replace('0','', 1) + '00001' #'0021600001'
        sql_table_1 = 'value_contributed_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        sql_table_2 = 'possessional_adjustments_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        for i in range(start_game, end_game + 1):
            game_id = game_id[:-len(str(i))]
            game_id = game_id + str(i)
            print('GAME #: ', i) #Print Current Game Being Evaluated
            value_contributed_boxscore, play_by_play_adjustments_df = compile_all(game_id, season, season_type, season_end_year, sql_upload)
            value_contributed_boxscore['Season_Type'] = 'Regular Season'
            play_by_play_adjustments_df['Season_Type'] = 'Regular Season'
            print(value_contributed_boxscore) #Print current game Value Contributed Box Score

            if  sql_upload == 'yes' or sql_upload == 'y' or sql_upload == 'Yes':
                columns_1 = [x.lower() for x in value_contributed_boxscore.columns]
                columns_1 = [x if x != 'to' else 'tos' for x in columns_1]
                copy_1_df = value_contributed_boxscore.copy()
                copy_1_df.columns = columns_1
                
                columns_2 = [x.lower() for x in play_by_play_adjustments_df.columns]
                columns_2 = [x if x != 'to' else 'tos' for x in columns_2]
                copy_2_df = play_by_play_adjustments_df.copy()
                copy_2_df.columns = columns_2

                conn = pg2.connect(dbname = 'postgres', host = "localhost")
                conn.autocommit = True
                engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
                copy_1_df.to_sql(sql_table_1, con = engine, if_exists= "append", index=False)
                copy_2_df.to_sql(sql_table_2, con = engine, if_exists= "append", index=False)
                conn.close()
            else:
                pass

        #sleep(60)
run_season('2019-20', 1, 1230, season_type="Playoffs", sql_upload='y', playoff_games_list='n')

# Need to figure out best way to pass year into general_df_func and play_by_play
''' #2018-19 Playoffs
['0041800101', '0041800102', '0041800103', '0041800104', '0041800111', '0041800112', '0041800113', '0041800114', 
'0041800115', '0041800121', '0041800122', '0041800123', '0041800124', '0041800125', '0041800131', '0041800132', 
'0041800133', '0041800134', '0041800141', '0041800142', '0041800143', '0041800144', '0041800145', '0041800146', 
'0041800151', '0041800152', '0041800153', '0041800154', '0041800155', '0041800156', '0041800157', '0041800161', 
'0041800162', '0041800163', '0041800164', '0041800165', '0041800171', '0041800172', '0041800173', '0041800174', 
'0041800175', '0041800201', '0041800202', '0041800203', '0041800204', '0041800205', '0041800211', '0041800212', 
'0041800213', '0041800214', '0041800215', '0041800216', '0041800217', '0041800221', '0041800222', '0041800223', 
'0041800224', '0041800225', '0041800226', '0041800231', '0041800232', '0041800233', '0041800234', '0041800235', 
'0041800236', '0041800237', '0041800301', '0041800302', '0041800303', '0041800304', '0041800305', '0041800306', 
'0041800311', '0041800312', '0041800313', '0041800314', '0041800401', '0041800402', '0041800403', '0041800404', 
'0041800405', '0041800406']
'''