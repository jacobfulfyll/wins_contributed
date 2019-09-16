from sqlalchemy import create_engine
import psycopg2 as pg2
from classes.BoxScore import BoxScoreTraditionalV2, BoxScoreMiscV2, BoxScoreScoringV2, BoxScoreAdvancedV2, BoxScorePlayerTrackV2
import pandas as pd

def general_df_func(game_id, winning_team, losing_team, season_type, season_end_year=None):
    ### Create DataFrame With All Players On Winning Team and Losing Team
    traditional = BoxScoreTraditionalV2(game_id=game_id)
    traditional_players_df = traditional.player_stats.get_data_frame()

    traditional_winning_players_df = traditional_players_df[traditional_players_df['TEAM_ID'] == winning_team]
    traditional_losing_players_df = traditional_players_df[traditional_players_df['TEAM_ID'] == losing_team]

    ### Create Winning anf Losing Team DataFrames With Players And Relevant Stats From Traditional Box Score ###
    winning_team_df = traditional_winning_players_df[['PLAYER_ID', 'PLAYER_NAME', 'MIN', 'FGM', 'FG3M', 'FTM', 'FTA', 'AST', 'STL', 'BLK','OREB', 'DREB', 'TO']]
    losing_team_df = traditional_losing_players_df[['PLAYER_ID', 'PLAYER_NAME', 'MIN', 'FGM', 'FG3M', 'FTM', 'FTA', 'AST', 'STL', 'BLK','OREB', 'DREB', 'TO']]

    ### Box Score Player Tracking Object and DataFrame For Winning Team ###
    tracking = BoxScorePlayerTrackV2(game_id=game_id)
    tracking_players_df = tracking.player_stats.get_data_frame()

    tracking_winning_players_df = tracking_players_df[tracking_players_df['TEAM_ID'] == winning_team]
    tracking_winning_players_df = tracking_winning_players_df[['PLAYER_ID', 'SAST', 'FTAST', 'DFGM', 'DFGA']]

    tracking_losing_players_df = tracking_players_df[tracking_players_df['TEAM_ID'] == losing_team]
    tracking_losing_players_df = tracking_losing_players_df[['PLAYER_ID', 'SAST', 'FTAST', 'DFGM', 'DFGA']]


    ### Merge Tracking Data With Current Data In Jacob Value DataFrame ###
    winning_team_df = pd.merge(winning_team_df, tracking_winning_players_df, on='PLAYER_ID', how='outer')
    losing_team_df = pd.merge(losing_team_df, tracking_losing_players_df, on='PLAYER_ID', how='outer')

    
    ### Box Score Player Scoring Object and DataFrame    ###
    scoring = BoxScoreScoringV2(game_id=game_id)
    scoring_players_df = scoring.sql_players_scoring.get_data_frame()
    
    scoring_winning_players_df = scoring_players_df[scoring_players_df['TEAM_ID'] == winning_team]
    scoring_winning_players_df = scoring_winning_players_df[['PLAYER_ID', 'PCT_UAST_2PM', 'PCT_UAST_3PM']]

    scoring_losing_players_df = scoring_players_df[scoring_players_df['TEAM_ID'] == losing_team]
    scoring_losing_players_df = scoring_losing_players_df[['PLAYER_ID', 'PCT_UAST_2PM', 'PCT_UAST_3PM']]


    ### Merge Scoring Data With Current Data In Jacob Value DataFrame ###
    winning_team_df = pd.merge(winning_team_df, scoring_winning_players_df, on='PLAYER_ID', how='outer')
    losing_team_df = pd.merge(losing_team_df, scoring_losing_players_df, on='PLAYER_ID', how='outer')


    ### Box Score Player Misc Object and DataFrame ###
    misc = BoxScoreMiscV2(game_id=game_id)
    misc_players_df = misc.sql_players_misc.get_data_frame()

    misc_winning_players_df = misc_players_df[misc_players_df['TEAM_ID'] == winning_team]
    misc_winning_players_df = misc_winning_players_df[['PLAYER_ID', 'PTS_2ND_CHANCE']]

    misc_losing_players_df = misc_players_df[misc_players_df['TEAM_ID'] == losing_team]
    misc_losing_players_df = misc_losing_players_df[['PLAYER_ID', 'PTS_2ND_CHANCE']]


    ### Calculate Def and Off Factor For Each Player ###

    advanced = BoxScoreAdvancedV2(game_id=game_id)
    player_advanced = advanced.player_stats.get_data_frame()

    team_advanced = advanced.team_stats.get_data_frame()

    advanced_winning_players_df = player_advanced[player_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = team_advanced[team_advanced['TEAM_ID'] == winning_team]
    advanced_winning_team_df = advanced_winning_team_df.reset_index()

    advanced_losing_players_df = player_advanced[player_advanced['TEAM_ID'] == losing_team]
    advanced_losing_team_df = team_advanced[team_advanced['TEAM_ID'] == losing_team]
    advanced_losing_team_df = advanced_losing_team_df.reset_index()

    pd.options.mode.chained_assignment = None

    advanced_winning_players_df['defense_factor'] = advanced_winning_players_df['DEF_RATING'] / advanced_winning_team_df.loc[0]['DEF_RATING']
    advanced_winning_players_df['defense_factor2'] = advanced_winning_players_df['defense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_winning_players_df['offense_factor'] = advanced_winning_players_df['OFF_RATING'] / advanced_winning_team_df.loc[0]['OFF_RATING']
    advanced_winning_players_df['offense_factor2'] = advanced_winning_players_df['offense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_winning_players_df = advanced_winning_players_df[['PLAYER_ID','defense_factor', 'defense_factor2', 'offense_factor', 'offense_factor2']]

    advanced_losing_players_df['defense_factor'] = advanced_losing_players_df['DEF_RATING'] / advanced_losing_team_df.loc[0]['DEF_RATING']
    advanced_losing_players_df['defense_factor2'] = advanced_losing_players_df['defense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_losing_players_df['offense_factor'] = advanced_losing_players_df['OFF_RATING'] / advanced_losing_team_df.loc[0]['OFF_RATING']
    advanced_losing_players_df['offense_factor2'] = advanced_losing_players_df['offense_factor'].apply(lambda x: 1 - (x - 1) if x > 1 else 1 + (1 - x))
    
    advanced_losing_players_df = advanced_losing_players_df[['PLAYER_ID','defense_factor', 'defense_factor2', 'offense_factor', 'offense_factor2']]


    ### Merge Misc and Advanced Data With Current Data In Jacob Value DataFrame ###
    winning_team_df = pd.merge(winning_team_df, misc_winning_players_df, on='PLAYER_ID', how='outer')
    winning_team_df = pd.merge(winning_team_df, advanced_winning_players_df, on='PLAYER_ID', how='outer')

    losing_team_df = pd.merge(losing_team_df, misc_losing_players_df, on='PLAYER_ID', how='outer')
    losing_team_df = pd.merge(losing_team_df, advanced_losing_players_df, on='PLAYER_ID', how='outer')
    
    ### Create FG2M Column and Drop FGM Column ###
    winning_team_df['FG2M'] = winning_team_df['FGM'] - winning_team_df['FG3M']
    losing_team_df['FG2M'] = losing_team_df['FGM'] - losing_team_df['FG3M']

    #print(winning_team_df)
    winning_team_df = winning_team_df.drop(columns='FGM')
    winning_team_df['DFG'] = winning_team_df['DFGA'] - winning_team_df['DFGM']
    winning_team_df = winning_team_df.fillna(0)

    ## Create a seconds column
    sec_list = []
    for idx, event in winning_team_df['MIN'].iteritems():
        min_split = str(event).split(':')
        if len(min_split) == 2:
            sec_list.append((int(min_split[0]) * 60 + int(min_split[1])) / 14400) #14400 are seconds in a basketball game for 5 players on a court at a time
        else:
            sec_list.append(0)

    winning_team_df['SEC_FACT'] = sec_list

    losing_team_df = losing_team_df.drop(columns='FGM')
    losing_team_df['DFG'] = losing_team_df['DFGA'] - losing_team_df['DFGM']
    losing_team_df = losing_team_df.fillna(0)

    ## Create a seconds column
    sec_list = []
    for idx, event in losing_team_df['MIN'].iteritems():
        min_split = str(event).split(':')
        if len(min_split) == 2:
            sec_list.append((int(min_split[0]) * 60 + int(min_split[1])) / 14400) #14400 are seconds in a basketball game for 5 players on a court at a time
        else:
            sec_list.append(0)

    losing_team_df['SEC_FACT'] = sec_list

    general_value_df = winning_team_df.append(losing_team_df, ignore_index=True)
    
    # Upload to SQL
    
    if season_end_year == None:
        next
    else:
        if season_type == 'Playoffs':
            sql_table = 'playoff_totals' + '_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]
        else:
            sql_table = 'totals' + '_' + str(season_end_year-1) + '_' + str(season_end_year)[-2:]

        columns = [x.lower() for x in general_value_df.columns]
        columns = [x if x != 'to' else 'tos' for x in columns]
        copy_df = general_value_df.copy()
        copy_df.columns = columns
        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
        copy_df.to_sql(sql_table, con = engine, if_exists= "append", index=False)
        conn.close()
    
    return [winning_team_df, losing_team_df]

