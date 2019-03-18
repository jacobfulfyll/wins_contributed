import pandas as pd
from classes.BoxScore import BoxScoreTraditionalV2
from classes.teamgamelog import TeamGameLog

def team_info(game_id, season):
    # Create Box Score Traditional Object
    traditional = BoxScoreTraditionalV2(game_id=game_id)
    
    # Get Box Score Traditional DataFrame
    teams_df = traditional.team_stats.get_data_frame()

    # Determine The Two Teams That Played In The Game #
    teams = teams_df['TEAM_ID'].unique()
    
    ### Figure Out Which Team Won The Game ###

        # Create a game log object for the first team in the teams list
    game_log = TeamGameLog(team_id=teams[0], season_all=season)
    game_log_df = game_log.team_game_log.get_data_frame()
    
        # Filter that teams game log to be only the specific game we are evaluating
    game_log_df = game_log_df[game_log_df['Game_ID'] == game_id]
    print(game_log_df.iloc[0]['GAME_DATE'], " ", game_log_df.iloc[0]['MATCHUP'], " ", game_log_df.iloc[0]['WL'])
    
        # If team[0] won the game, set their id to the winning_team variable, else set team[1]
    if game_log_df.iloc[0]['WL'] == 'W' and '@' in game_log_df.iloc[0]['MATCHUP']:
        winning_team = teams[0]
        losing_team = teams[1]
        home_away = 1
    elif game_log_df.iloc[0]['WL'] == 'W' and '@' not in game_log_df.iloc[0]['MATCHUP']:
        winning_team = teams[0]
        losing_team = teams[1]
        home_away = 0 
    elif game_log_df.iloc[0]['WL'] == 'L' and '@' not in game_log_df.iloc[0]['MATCHUP']:
        winning_team = teams[1]
        losing_team = teams[0]
        home_away = 1
    else:
        winning_team = teams[1]
        losing_team = teams[0]
        home_away = 0

    return losing_team, winning_team, home_away