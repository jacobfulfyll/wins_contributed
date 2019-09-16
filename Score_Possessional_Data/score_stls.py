import pandas as pd

#Steals Value Structure

block_before = .5

def score_stls(player_events_df, game_df, current_player, win_loss, team_id, defense_possession_value):
    current_player_stls_score = 0
    
    if win_loss == 1:
        team1 = 'WINNINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
    
    # Filter player_events_df to be just plays where player caused a turnover
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 5) & (player_events_df['PLAYER2_ID'] == current_player)]
    
    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every caused turnover
        counter = 1
        while True:
            if (idx == 0 # If previous row was one of these things, there was a change of possession
            or (idx - counter) <= 0 #Index out of scope
            or game_df.loc[idx - counter]['EVENTMSGTYPE'] == 5 # Turnover
            or game_df.loc[idx - counter]['EVENTMSGTYPE'] == 1): # Made shot
                current_player_stls_score += defense_possession_value
                break

            elif (game_df.loc[idx - counter]['EVENTMSGTYPE'] == 2 # If there was a made shot by the winning team, there was a change of possession
            and game_df.loc[idx - counter][team1] != None):
                current_player_stls_score += defense_possession_value
                break

            elif 'block' in str(game_df.loc[idx - counter][team1]).lower(): # If there was a block before a change of possession
                current_player_stls_score += defense_possession_value * block_before
                break

            else:
                counter += 1 #Cycle through rows
    
    
    if current_player_stls_score is None:
        current_player_stls_score = 0
    
    if current_player_stls_score is None:
        current_player_stls_score = 0
    
    return current_player_stls_score
