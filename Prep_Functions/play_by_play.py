from sqlalchemy import create_engine
import psycopg2 as pg2
from classes.PlaybyPlay import PlayByPlayV2


def game_df_func(game_id, home_away, season_end_year=None):
    # Create play_by_play object for current game
    play_by_play = PlayByPlayV2(game_id=game_id)

    play_by_play_df = play_by_play.play_by_play.get_data_frame()
    play_by_play_df['GAME_ID'] = game_id
    # Include only relevant columns in game_df
    game_df = play_by_play_df[['GAME_ID','EVENTNUM','EVENTMSGTYPE','HOMEDESCRIPTION', 'VISITORDESCRIPTION', 'PLAYER1_NAME', 'PLAYER2_NAME', 'PLAYER1_ID', 'PLAYER2_ID', 'PLAYER1_TEAM_ID', 'PLAYER2_TEAM_ID']]
    
    # Filter out irrelevant message types
    game_df = game_df[game_df['EVENTMSGTYPE'] != 8]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 9]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 10]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 11]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 12]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 13]
    game_df = game_df[game_df['EVENTMSGTYPE'] != 18]
    
    # Reset game_df index
    game_df = game_df.reset_index().drop(columns='index')
    
    # Upload to SQL

    if season_end_year ==  None:
        next
    else:
        sql_table = 'play_by_play_' + str(season_end_year)
        columns = [x.lower() for x in game_df.columns]
        store_df = game_df.copy()
        store_df.columns = columns
        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://owner:Fulfyll@localhost/jacob_wins')
        store_df.to_sql(sql_table, con = engine, if_exists= "append", index=False)
        conn.close()

    if home_away == 0:
        game_df = game_df.rename({"HOMEDESCRIPTION": "WINNINGTEAM", "VISITORDESCRIPTION": "LOSINGTEAM"}, axis=1)
    else:
        game_df = game_df.rename({"HOMEDESCRIPTION": "LOSINGTEAM", "VISITORDESCRIPTION": "WINNINGTEAM"}, axis=1)
    
    
    return game_df