import pandas as pd
from nba_api.stats.endpoints import boxscoretraditionalv2, teamgamelog

def get_team_info(game_id, season, season_type):
    # Create Box Score Traditional Object and get DataFrame

    # print(type(game_id))
    traditional = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    teams_df = traditional.team_stats.get_data_frame()

    # Determine The Two Teams That Played In The Game #
    teams = teams_df['TEAM_ID'].unique()

    ### Figure Out Which Team Won The Game ###

        # Create a game log object and dataframe for the first team in the teams list
    game_log = teamgamelog.TeamGameLog(team_id=teams[0], season=season, season_type_all_star=season_type)
    game_log_df = game_log.team_game_log.get_data_frame()

        # Filter that teams game log to be only the specific game we are evaluating
    game_log_df = game_log_df[game_log_df['Game_ID'] == game_id]
        # Print basic info about the game for tracking purposes as code is running, game date, two teams playing, if first team won or lost game  
    print(game_log_df.iloc[0]['GAME_DATE'], " ", game_log_df.iloc[0]['MATCHUP'], " ", game_log_df.iloc[0]['WL'])
    
        # If team[0] won the game, set their id to the winning_team variable, else set team[1]
        # If there is an @ the first team is away, else they are home. This is important for the play_by_play dataframe
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