from sqlalchemy import create_engine
import psycopg2 as pg2
from nba_api.stats.endpoints import boxscoretraditionalv2, boxscoremiscv2, boxscorescoringv2, boxscoreplayertrackv2, boxscoreadvancedv2
import pandas as pd

def get_value_contributed_inputs(game_id, winning_team, losing_team, season_type, season_end_year, sql_upload='no'):
    ### Create DataFrame With All Players On Winning Team and Losing Team
    traditional = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    traditional_players_df = traditional.player_stats.get_data_frame()

    ##Create a seconds factor column. How many seconds each player played as a percentage of how many seconds there are to go around on each team
    sec_list = []
    for idx, event in traditional_players_df['MIN'].iteritems():
        min_split = str(event).split(':')
        if len(min_split) == 2:
            sec_list.append((int(min_split[0]) * 60 + int(min_split[1])) / 14400) #14400 are seconds in a basketball game for 5 players on a court at a time
        else:
            sec_list.append(0)

    traditional_players_df['SEC_FACT'] = sec_list
    traditional_players_df['FG2_MADE'] = traditional_players_df['FGM'] - traditional_players_df['FG3M']
    traditional_players_df['FG2_MISSED'] = traditional_players_df['FGA'] - traditional_players_df['FG3A'] - traditional_players_df['FG2_MADE']
    traditional_players_df['FG3_MADE'] = traditional_players_df['FG3M']
    traditional_players_df['FG3_MISSED'] = traditional_players_df['FG3A'] - traditional_players_df['FG3M']

    traditional_players_df = traditional_players_df[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'SEC_FACT', 'FG2_MADE', 'FG2_MISSED', 'FG3_MADE', 'FG3_MISSED', 'FTM', 'FTA', 'AST', 'STL', 'BLK','OREB', 'DREB', 'TO']]

    ### Box Score Player Tracking Object and DataFrame For Winning Team ###
    tracking = boxscoreplayertrackv2.BoxScorePlayerTrackV2(game_id=game_id)
    tracking_players_df = tracking.player_stats.get_data_frame()

        # Calculate how many field goals players successfully defended
    tracking_players_df['DFG'] = tracking_players_df['DFGA'] - tracking_players_df['DFGM']
    tracking_players_df = tracking_players_df[['PLAYER_ID', 'SAST', 'FTAST', 'DFG']]

    ### Merge Tracking Data With Current Data In Jacob Value DataFrame ###
    val_contr_inputs_df = pd.merge(traditional_players_df, tracking_players_df, on='PLAYER_ID', how='outer')
    
    ### Box Score Player Scoring Object and DataFrame    ###
    scoring = boxscorescoringv2.BoxScoreScoringV2(game_id=game_id)
    scoring_players_df = scoring.sql_players_scoring.get_data_frame()
    scoring_players_df = scoring_players_df[['PLAYER_ID', 'PCT_UAST_2PM', 'PCT_UAST_3PM']]
    val_contr_inputs_df = pd.merge(val_contr_inputs_df, scoring_players_df, on='PLAYER_ID', how='outer')

    ### Box Score Player Misc Object and DataFrame ###
    misc = boxscoremiscv2.BoxScoreMiscV2(game_id=game_id)
    misc_players_df = misc.sql_players_misc.get_data_frame()
    misc_players_df = misc_players_df[['PLAYER_ID', 'PTS_2ND_CHANCE']]
    val_contr_inputs_df = pd.merge(val_contr_inputs_df, misc_players_df, on='PLAYER_ID', how='outer')

    ### Calculate Def and Off Factor For Each Player ###
    advanced = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id)
    player_advanced = advanced.player_stats.get_data_frame()
    team_advanced = advanced.team_stats.get_data_frame()

    advanced_winning_players_df = player_advanced[player_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = team_advanced[team_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = advanced_winning_team_df.reset_index()
    # print(advanced_winning_players_df[['PLAYER_NAME','OFF_RATING', 'DEF_RATING']])
    # print(advanced_winning_team_df[['TEAM_NAME','OFF_RATING', 'DEF_RATING']])

    advanced_losing_players_df = player_advanced[player_advanced['TEAM_ID'] == losing_team]
    advanced_losing_team_df = team_advanced[team_advanced['TEAM_ID'] == losing_team]
    advanced_losing_team_df = advanced_losing_team_df.reset_index()
    # print(advanced_losing_players_df[['PLAYER_NAME','OFF_RATING', 'DEF_RATING']])
    # print(advanced_losing_team_df[['TEAM_NAME','OFF_RATING', 'DEF_RATING']])

    pd.options.mode.chained_assignment = None

    advanced_winning_players_df['defense_factor'] = advanced_winning_players_df['DEF_RATING'] / advanced_winning_team_df.loc[0]['DEF_RATING']
    advanced_winning_players_df['defense_factor'] = advanced_winning_players_df['defense_factor'].apply(lambda x: 1 - (x - 1))
    
    advanced_winning_players_df['offense_factor'] = advanced_winning_players_df['OFF_RATING'] / advanced_winning_team_df.loc[0]['OFF_RATING']
    
    advanced_winning_players_df = advanced_winning_players_df[['PLAYER_ID','defense_factor', 'offense_factor']]

    advanced_losing_players_df['defense_factor'] = advanced_losing_players_df['DEF_RATING'] / advanced_losing_team_df.loc[0]['DEF_RATING']
    advanced_losing_players_df['defense_factor'] = advanced_losing_players_df['defense_factor'].apply(lambda x: 1 - (x - 1))
    
    advanced_losing_players_df['offense_factor'] = advanced_losing_players_df['OFF_RATING'] / advanced_losing_team_df.loc[0]['OFF_RATING']
    
    advanced_losing_players_df = advanced_losing_players_df[['PLAYER_ID','defense_factor','offense_factor']]

    ### Merge Advanced Data With Current Data In Jacob Value DataFrame ###
    advanced_players_df = advanced_winning_players_df.append(advanced_losing_players_df, ignore_index=True)
    val_contr_inputs_df = pd.merge(val_contr_inputs_df, advanced_players_df, on='PLAYER_ID', how='outer')

    #print(winning_team_df)
    #Assume that if there is an n/a the player did not do anything in that statistical category or did not play
    val_contr_inputs_df = val_contr_inputs_df.fillna(0).reset_index(drop=True)
    # print(val_contr_inputs_df)
    winning_team_df = val_contr_inputs_df[val_contr_inputs_df['TEAM_ID'] == winning_team].reset_index(drop=True)
    losing_team_df = val_contr_inputs_df[val_contr_inputs_df['TEAM_ID'] == losing_team].reset_index(drop=True)
    
    if season_type == 'Playoffs':
        val_contr_inputs_df['SEASON_TYPE'] = 'Playoffs'
    else:
        val_contr_inputs_df['SEASON_TYPE'] = 'Regular Season'

    # print(val_contr_inputs_df.columns)

    # Upload to SQL
    if sql_upload == 'no':
        pass
    else:
        sql_table = 'val_contr_inputs' + '_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]

        columns = [x.lower() for x in val_contr_inputs_df.columns]
        columns = [x if x != 'to' else 'tos' for x in columns]
        
        copy_df = val_contr_inputs_df.copy()
        copy_df.columns = columns
        
        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
        copy_df.to_sql(sql_table, con = engine, if_exists= "append", index=False)
        conn.close()
    
    return [winning_team_df, losing_team_df]

