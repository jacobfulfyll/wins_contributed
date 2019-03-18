import sys
import pandas as pd
import numpy as np
import psycopg2 as pg2
from sqlalchemy import create_engine
from time import sleep
from Prep_Functions.boxscore_inputs import general_df_func
from Prep_Functions.find_teams import  team_info
from Prep_Functions.game_possession_info import possession_variables
from Prep_Functions.play_by_play import game_df_func
from run_game import one_game_wins


def compile_all(game_id_start, game_id_end, season):
        #Create df
    all_games_df = pd.DataFrame(columns=['game_id', 'team_id', 'opponent_id', 'player_id','player_name','points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr'])
    game_id_start = int(game_id_start)
    game_id_end = int(game_id_end)
    counter = 0
    current_game_id = game_id_start + counter

    # Run until all games passed in have been run
    while current_game_id <= game_id_end:
        current_game_id = game_id_start + counter
        str_game_id = '00' + str(current_game_id)

        # Call Helper Functions
        losing_team, winning_team, home_away = team_info(str_game_id, season)
        general_df = general_df_func(str_game_id, winning_team)
        #print(general_df)
        game_df = game_df_func(str_game_id, home_away)
        #print(game_df)
        jacob_game_stat_df = one_game_wins(str_game_id, game_df, general_df, winning_team, home_away, winning_team, losing_team)
        # Append current game to previous game to create one df
        all_games_df = all_games_df.append(jacob_game_stat_df)

        counter += 1
    all_games_df = all_games_df.reset_index()
    all_games_df = all_games_df.drop(columns='index')

    return all_games_df[['game_id','team_id', 'opponent_id', 'player_id', 'player_name', 'points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr']]


def run_season(season, end_game):
    game_id = '0021600001'

    for i in range(117, end_game + 1, 2):
        game_id = game_id[:-len(str(i))]
        game_id = game_id + str(i)
        print('GAME #: ', i)
        jacob_wins_df = compile_all(game_id, game_id, season)
        print(jacob_wins_df)

        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://owner:Fulfyll@localhost/jacob_wins')
        jacob_wins_df.to_sql("jacob_wins_2017_final", con = engine, if_exists= "append", index=False)
        conn.close()

        #sleep(10)
run_season('2016-17', 1230)

# Must Change sql table name, game_id variable along with run season function call
# Need to figure out best way to pass year into general_df_func and play_by_play
