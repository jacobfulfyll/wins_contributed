import pandas as pd


def score_to(player_events_df, game_df, current_player, home_away, team_id, offense_possession_value):
    # Make player df alle events where player committed a turnover
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 5) & (player_events_df['PLAYER1_ID'] == current_player)]
    
    # Since turnovers always receive full posession value loss, multiple the length by the possession value
    current_player_tos_score = len(player_events_df['EVENTMSGTYPE']) * offense_possession_value

    if current_player_tos_score is None:
        current_player_tos_score = 0
    if current_player_tos_score is None:
        current_player_tos_score = 0
    return -current_player_tos_score