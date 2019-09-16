from classes.BoxScore import BoxScoreTraditionalV2


def possession_variables(game_id, winning_team, losing_team, current_team):
    # Create Box Score Traditional Object
    traditional = BoxScoreTraditionalV2(game_id=game_id)
    
    # Teams Dataframe
    traditional_team_df = traditional.team_stats.get_data_frame()
    
    # Winning Team Dataframe
    winning_team_df = traditional_team_df[traditional_team_df['TEAM_ID'] == winning_team]
    winning_team_df = winning_team_df.reset_index()

    # Losing Team Dataframe
    losing_team_df = traditional_team_df[traditional_team_df['TEAM_ID'] == losing_team]
    losing_team_df = losing_team_df.reset_index()

    # Winning Team Field Goal Info
    winner_fg_points = (winning_team_df.loc[0]['FGM'] - winning_team_df.loc[0]['FG3M']) * 2 + winning_team_df.loc[0]['FG3M'] * 3
    winner_fg_att = winning_team_df.loc[0]['FGA'] 

    # Losing Team Field Goal Info
    loser_fg_points = (losing_team_df.loc[0]['FGM'] - losing_team_df.loc[0]['FG3M']) * 2 + losing_team_df.loc[0]['FG3M'] * 3
    loser_fg_att = losing_team_df.loc[0]['FGA'] 
    
    # Winner Possession Value Calculations
    winner_effective_ft_pct = winning_team_df.loc[0]['FT_PCT']
    winner_offense_possession_value = (winner_fg_points + winning_team_df.loc[0]['FTM']) / (winner_fg_att + winning_team_df.loc[0]['TO'] + (winning_team_df.loc[0]['FTA'] / 2)  - 1) # Minus 1 on attempts to subtract the missed shot in question, add in turnovers and free throws because you are effectively preventing another possession
    winner_defense_possession_value = (loser_fg_points + losing_team_df.loc[0]['FTM']) / (loser_fg_att + losing_team_df.loc[0]['TO'] + (losing_team_df.loc[0]['FTA'] / 2)  - 1) # Minus 1 on attempts to subtract the missed shot in question, add in turnovers and free throws because you are effectively preventing another possession

    # Loser Possession Value Calculations
    loser_effective_ft_pct = losing_team_df.loc[0]['FT_PCT']
    loser_offense_possession_value = (loser_fg_points + winning_team_df.loc[0]['FTM']) / (loser_fg_att + losing_team_df.loc[0]['TO'] + (losing_team_df.loc[0]['FTA'] / 2)  - 1) # Minus 1 on attempts to subtract the missed shot in question, add in turnovers and free throws because you are effectively preventing another possession
    loser_defense_possession_value = (winner_fg_points + losing_team_df.loc[0]['FTM']) / (winner_fg_att + winning_team_df.loc[0]['TO'] + (winning_team_df.loc[0]['FTA'] / 2)  - 1) # Minus 1 on attempts to subtract the missed shot in question, add in turnovers and free throws because you are effectively preventing another possession    
    
    if current_team == 1:
        return winner_offense_possession_value, winner_defense_possession_value, winner_effective_ft_pct
    else:
        return loser_offense_possession_value, loser_defense_possession_value, loser_effective_ft_pct 