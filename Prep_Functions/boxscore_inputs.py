import pandas as pd
from sqlalchemy import create_engine
import psycopg2 as pg2
from classes.BoxScore import BoxScoreTraditionalV2, BoxScoreMiscV2, BoxScoreScoringV2, BoxScoreAdvancedV2, BoxScorePlayerTrackV2



def general_df_func(game_id, winning_team, season_end_year=None):
    ### Create DataFrame With All Players On Winning Team
    traditional = BoxScoreTraditionalV2(game_id=game_id)
    traditional_players_df = traditional.player_stats.get_data_frame()
    traditional_winning_players_df = traditional_players_df[traditional_players_df['TEAM_ID'] == winning_team]

    ### Create Jacob Value DataFrame With Winning Players And Relevant Stats From Traditional Box Score ###
    jacob_value_df = traditional_winning_players_df[['PLAYER_ID', 'PLAYER_NAME', 'MIN', 'FGM', 'FG3M', 'FTM', 'FTA', 'AST', 'STL', 'BLK','OREB', 'DREB', 'TO']]

    ### Box Score Player Tracking Object and DataFrame For Winning Team ###
    tracking = BoxScorePlayerTrackV2(game_id=game_id)
    tracking_players_df = tracking.player_stats.get_data_frame()
    tracking_winning_players_df = tracking_players_df[tracking_players_df['TEAM_ID'] == winning_team]
    tracking_winning_players_df = tracking_winning_players_df[['PLAYER_ID', 'SAST', 'FTAST', 'DFGM', 'DFGA']]


    ### Merge Tracking Data With Current Data In Jacob Value DataFrame ###
    jacob_value_df = pd.merge(jacob_value_df, tracking_winning_players_df, on='PLAYER_ID', how='outer')


    ### Box Score Player Scoring Object and DataFrame For Winning Team ###
    scoring = BoxScoreScoringV2(game_id=game_id)
    scoring_players_df = scoring.sql_players_scoring.get_data_frame()
    scoring_winning_players_df = scoring_players_df[scoring_players_df['TEAM_ID'] == winning_team]
    scoring_winning_players_df = scoring_winning_players_df[['PLAYER_ID', 'PCT_UAST_2PM', 'PCT_UAST_3PM']]

    ### Merge Scoring Data With Current Data In Jacob Value DataFrame ###
    jacob_value_df = pd.merge(jacob_value_df, scoring_winning_players_df, on='PLAYER_ID', how='outer')


    ### Box Score Player Misc Object and DataFrame For Winning Team ###
    misc = BoxScoreMiscV2(game_id=game_id)
    misc_players_df = misc.sql_players_misc.get_data_frame()
    misc_winning_players_df = misc_players_df[misc_players_df['TEAM_ID'] == winning_team]
    misc_winning_players_df = misc_winning_players_df[['PLAYER_ID', 'PTS_2ND_CHANCE']]

    ### Calculate Def and Off Factor For Each Player ###

    advanced = BoxScoreAdvancedV2(game_id=game_id)
    player_advanced = advanced.player_stats.get_data_frame()

    team_advanced = advanced.team_stats.get_data_frame()

    advanced_winning_players_df = player_advanced[player_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = team_advanced[team_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = advanced_winning_team_df.reset_index()

    pd.options.mode.chained_assignment = None

    advanced_winning_players_df['defense_factor'] = advanced_winning_players_df['DEF_RATING'] / advanced_winning_team_df.loc[0]['DEF_RATING']
    advanced_winning_players_df['defense_factor2'] = advanced_winning_players_df['defense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_winning_players_df['offense_factor'] = advanced_winning_players_df['OFF_RATING'] / advanced_winning_team_df.loc[0]['OFF_RATING']
    advanced_winning_players_df['offense_factor2'] = advanced_winning_players_df['offense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_winning_players_df = advanced_winning_players_df[['PLAYER_ID','defense_factor', 'defense_factor2', 'offense_factor', 'offense_factor2']]


    ### Merge Misc Data With Current Data In Jacob Value DataFrame ###
    jacob_value_df = pd.merge(jacob_value_df, misc_winning_players_df, on='PLAYER_ID', how='outer')
    jacob_value_df = pd.merge(jacob_value_df, advanced_winning_players_df, on='PLAYER_ID', how='outer')
    
    ### Create FG2M Column and Drop FGM Column ###
    jacob_value_df['FG2M'] = jacob_value_df['FGM'] - jacob_value_df['FG3M']
    #print(jacob_value_df)
    general_value_df = jacob_value_df.drop(columns='FGM')
    general_value_df['DFG'] = general_value_df['DFGA'] - general_value_df['DFGM']
    general_value_df = general_value_df.fillna(0)

    ## Create a seconds column
    sec_list = []
    for idx, event in general_value_df['MIN'].iteritems():
        min_split = str(event).split(':')
        if len(min_split) == 2:
            sec_list.append((int(min_split[0]) * 60 + int(min_split[1])) / 14400) #14400 are seconds in a basketball game for 5 players on a court at a time
        else:
            sec_list.append(0)

    general_value_df['SEC_FACT'] = sec_list
    
    # Upload to SQL

    if season_end_year == None:
        next
    else:
        sql_table = 'general ' + str(season_end_year)
        columns = [x.lower() for x in general_value_df.columns]
        columns = [x if x != 'to' else 'tos' for x in columns]
        copy_df = general_value_df.copy()
        copy_df.columns = columns
        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://owner:Fulfyll@localhost/jacob_wins')
        copy_df.to_sql(sql_table, con = engine, if_exists= "append", index=False)
        conn.close()
    
    return general_value_df