import pandas as pd

# Made Field Goals Value Structure
Assisted_FG = .7
Assisted_FG_After_OREB = .4
FG_After_OREB = .5


# Run this function for every player who made a field goal
def score_points(player_events_df, game_df, current_player, home_away, team_id, offense_possession_value):
    current_player_points_score = 0
    
    # Limit player_events_df to only made_fg related rows. EVENTMSGTYPE 1 = Made Shot
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 1) & (player_events_df['PLAYER1_ID'] == current_player)]

    # game_df and player_events_df have the same index
    # game_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case assists
    # Moving up game_df means looking at events which happened before the result being analyzed in the player_events_df
       # In regards to points, this means looking for offensive rebounds which happened previously within the same possession

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every made field goal by this player
        o_board_index = 1 # o_board_index is a counter which looks for offensive rebounds
        
        if (idx == 0 
        or (idx - o_board_index) == 0  # Will throw error if you are looking for an index < 0
        or (game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3 or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1 or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5)): # If the event above is a free throw, another made shot, or a turnover there was no o-reb on this possession
                
                if 'ast' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): # If the shot was unassisted
                    if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): # If the shot was not a 3 pointer
                        current_player_points_score += 2 - offense_possession_value
                    else:
                        current_player_points_score += 3 - offense_possession_value
                        
                else:
                    if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): #If the shot was assisted 2 pointer
                        current_player_points_score += (2 - offense_possession_value) * Assisted_FG
                    else:
                        current_player_points_score += (3 - offense_possession_value) * Assisted_FG
        
        else: # Look for offensive rebounds earlier in the possession
            while True:
                if (idx == 0 
                or (idx - o_board_index) == 0 
                or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 2 
                or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3
                or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5): # Find the row with the last missed shot or turnover
                    break
                else: 
                    o_board_index += 1
            if game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5: # If there was a turnover, there were no offensive rebounds on the possession
                if 'ast' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): # If the shot was not assisted
                    if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): # If the shot was not a 3 pointer
                        current_player_points_score += 2 - offense_possession_value
                    else:
                        current_player_points_score += 3 - offense_possession_value
                        
                else:
                    if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): #If the shot was assisted 2 pointer
                        current_player_points_score += (2 - offense_possession_value) * Assisted_FG
                    else:
                        current_player_points_score += (3 - offense_possession_value) * Assisted_FG

            if (game_df.loc[idx - o_board_index]['WINNINGTEAM'] == None 
            or 'miss' in str(game_df.loc[idx - o_board_index]['LOSINGTEAM']).lower()): # If the row with the last missed shot was from the losing team, there were no offensive rebounds
                    
                    if 'ast' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                        if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower(): 
                            current_player_points_score += 2 - offense_possession_value
                        else:
                            current_player_points_score += 3 - offense_possession_value
                    else:
                        if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                            
                            current_player_points_score += (2 - offense_possession_value) * Assisted_FG
                        else:
                            current_player_points_score += (3 - offense_possession_value) * Assisted_FG
            
            elif ('miss' in str(game_df.loc[idx - o_board_index]['WINNINGTEAM']).lower() 
            and game_df.loc[idx - o_board_index + 1]['EVENTMSGTYPE'] == 4 
            and 'rebound' in str(game_df.loc[idx - o_board_index + 1]['WINNINGTEAM']).lower()): # If the last shot missed was from the winning team and was followed by a rebound, there was an offensive rebound in the possession
                    
                    if 'ast' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                        
                        if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                            current_player_points_score += (2 - offense_possession_value) * FG_After_OREB
                            
                        else:
                            current_player_points_score += (3 - offense_possession_value) * FG_After_OREB
                            
                    else:
                        if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                            current_player_points_score += (2 - offense_possession_value) * Assisted_FG_After_OREB
                            
                        else:
                            current_player_points_score += (3 - offense_possession_value) * Assisted_FG_After_OREB
                            
            else:
                continue
    
    #If there is an n/a return 0, else return the player's score
    if current_player_points_score is None:
        return 0
    else:
        
        return current_player_points_score