from sqlalchemy import create_engine
import psycopg2 as pg2
from nba_api.stats.endpoints import playbyplayv2
import pandas as pd


def get_play_by_play_df(game_id, home_away, season_type, season_end_year=None, sql_upload='no'):
    # Create play_by_play object for current game
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=game_id)

    play_by_play_df = play_by_play.play_by_play.get_data_frame()
    play_by_play_df['GAME_ID'] = game_id
    # Include only relevant columns in game_df
    play_by_play_df = play_by_play_df[['GAME_ID','EVENTNUM','EVENTMSGTYPE','HOMEDESCRIPTION', 'VISITORDESCRIPTION', 'PLAYER1_NAME', 'PLAYER2_NAME', 'PLAYER1_ID', 'PLAYER2_ID', 'PLAYER1_TEAM_ID', 'PLAYER2_TEAM_ID']]
    
    # Filter out irrelevant message types
    filter_msg_types_list = [8,9,10,11,12,13,18]
    for msg_type in filter_msg_types_list:
        play_by_play_df = play_by_play_df[play_by_play_df['EVENTMSGTYPE'] != msg_type]
    
    # Reset play_by_play_df index
    play_by_play_df = play_by_play_df.reset_index(drop=True)

    if season_type == 'Playoffs':
        play_by_play_df['SEASON_TYPE'] = 'Playoffs'
    else:
        play_by_play_df['SEASON_TYPE'] = 'Regular Season'

    if home_away == 0:
        play_by_play_df = play_by_play_df.rename({"HOMEDESCRIPTION": "WINNINGTEAM", "VISITORDESCRIPTION": "LOSINGTEAM"}, axis=1)
    else:
        play_by_play_df = play_by_play_df.rename({"HOMEDESCRIPTION": "LOSINGTEAM", "VISITORDESCRIPTION": "WINNINGTEAM"}, axis=1)
    
    # Upload to SQL
    if sql_upload == 'no':
        pass
    else:
        sql_table = 'play_by_play' + '_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        
        columns = [x.lower() for x in play_by_play_df.columns]
        store_df = play_by_play_df.copy()
        store_df.columns = columns
        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
        store_df.to_sql(sql_table, con = engine, if_exists= "append", index=False)
        conn.close()
    

    return play_by_play_df