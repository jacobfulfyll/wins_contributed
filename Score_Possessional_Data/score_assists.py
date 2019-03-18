import pandas as pd

# Assist Value Structure:

Assist = .3 # Assists receive 30% of value created from made shot when no offensive rebound
Assisted_After_OREB = .2 # Assists receive 20% of value created from made shot when after offensive rebound

# Run this function for every player who had an assist within a given game
def score_assists(player_events_df, game_df, current_player, home_away, team_id, offense_possession_value):
    current_player_assists_score = 0 # Assists score for current player

    # Limit player_events_df to only assist related rows. EVENTMSGTYPE 1 = Made Shot
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 1) 
                       & (player_events_df['PLAYER2_ID'] == current_player)]


    # game_df and player_events_df have the same indexes
    # game_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case assists
    # Moving up game_df means looking at events which happened before the result being analyzed in the player_events_df
       # In regards to assists, this means looking for offensive rebounds which happened previously within the same possession

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every assist by this player in this game
        o_board_index = 1 # Counter
        if (idx == 0                                                 # If index = 0, there were no offensive rebounds before this assist
        or (idx - o_board_index) == 0                                # If when moving up the dataframe, we hit index 0, there was not an offensive rebound before this assist
        or (game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3    # If there was a free throw attempt before an assist and we haven't seen a rebound, there was no offensive rebound within the possession
        or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1     # If there was a made shot before this assist, there was no offensive rebound on this possession
        or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5)):  # If there was a turnover before this assist, there was no offensive rebound on this possession
            if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():      # If '3pt' is not in the assist event we are looking at, make the points scored on the possession 2 
                current_player_assists_score += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            else:                                                                       # If '3pt' was in the assist event, make points scored on the possession 3
                current_player_assists_score += (3 - offense_possession_value) * Assist # Add the value created to assisters current assist score
        
        # If any of those events weren't the previous event, we can't say there was no offensive rebound prior
        # Keep running up the chain to find either an offensive rebound or a stop event which represents a change in possession

        else: 
            while True:
                if (idx == 0
                or (idx - o_board_index) == 0
                or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 2
                or game_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3): # Go up the chain until you find the last missed shot or free throw, because an offensive rebound can only happen on a missed shot or free throw
                    break
                else: 
                    o_board_index += 1 # Increasing o_board_index lets you keep moving up the events in game_df

            if (game_df.loc[idx - o_board_index]['WINNINGTEAM'] == None 
            or 'miss' in str(game_df.loc[idx - o_board_index]['LOSINGTEAM']).lower()): # If the last missed shot was from the losing team, there was no offensive rebound on this possession
                if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                    current_player_assists_score += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
                else:
                    current_player_assists_score += (3 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            
            elif ('miss' in str(game_df.loc[idx - o_board_index]['WINNINGTEAM']).lower() 
            and game_df.loc[idx - o_board_index + 1]['EVENTMSGTYPE'] == 4
            and 'rebound' in str(game_df.loc[idx - o_board_index + 1]['WINNINGTEAM']).lower()): # If the last missed shot was rebounded by the winning team, there was an offensive rebound on the possession
                if '3pt' not in str(player_events_df.loc[idx]['WINNINGTEAM']).lower():
                    current_player_assists_score += (2 - offense_possession_value) * Assisted_After_OREB # Add the value created on the possession, multiply by the offensive rebound with assit factor rather than the assist factor
                else:
                    current_player_assists_score += (3 - offense_possession_value) * Assisted_After_OREB  # Add the value created on the possession, multiply by the offensive rebound with assit factor rather than the assist factor 
            else:
                continue
    if current_player_assists_score is None:
        return 0
    else:
        
        return current_player_assists_score # Return the assists score for the current player
