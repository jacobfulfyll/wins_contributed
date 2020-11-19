import pandas as pd

# Free Throw Value Structure:

Assisted_FT = .7
Assissted_FT_After_OREB = .4
FT_After_OREB = .5

# Run this function for every player who has a FT within a given game
def score_ft(player_events_df, play_by_play_df, current_player, win_loss, team_id, offense_possession_value):
    current_player_ft_positive = 0
    current_player_ft_negative = 0

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'

    # Limit player_events_df to only FT related rows. EVENTMSGTYPE 3 = FT Attempt
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 3) & (player_events_df['PLAYER1_ID'] == current_player)]
    
    previous_idx = 'n/a'
    remove_idx = []
    for idx in player_events_df.index:
        if previous_idx == idx - 1:
            remove_idx.append(idx)
            previous_idx = idx
        else:
            previous_idx = idx

    player_events_df = player_events_df.drop(remove_idx)
    
    # play_by_play_df and player_events_df have the same indexes
    # play_by_play_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case assists
    # Moving up play_by_play_df means looking at events which happened before the result being analyzed in the player_events_df
       # In regards to FT, this means looking for offensive rebounds and assists which happened previously within the same possession
    # Moving down play_by_play_df means looking at events which happened after free throw
       # This is used to determine how many free throws were made

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every time a player is sent to the line
        counter = 0
        points_on_board = 0
        o_board_index = 2 # Value starts at 2, because the row above the free throw is always a foul
        oreb_sequence = 0
        if 'technical' in str(play_by_play_df.loc[idx][team1]).lower():
            if 'miss' not in str(play_by_play_df.loc[idx][team1]).lower():
                current_player_ft_positive += 1
                continue
            else:
                continue
        if idx - 2 <= 0: # If index is out of range, there are no assists
            ast = 0
        elif 'ast' in str(play_by_play_df.loc[idx - 2][team1]).lower(): # Check for an assist on the free throw
            ast = 1
        else:
            ast = 0 

        if 'of 1' in str(play_by_play_df.loc[idx][team1]).lower(): # Number of free throws
            if 'miss' not in str(play_by_play_df.loc[idx][team1]).lower():
                current_player_ft_positive += 1
                continue
            else:
                continue
        elif 'of 2' in str(play_by_play_df.loc[idx][team1]).lower(): # Number of free throws
            free_throws = 2
        elif 'of 3' in str(play_by_play_df.loc[idx][team1]).lower(): # Number of free throws
            free_throws = 3
        else:
            # print(str(play_by_play_df.loc[idx][team1]))
            # print('FREE THROW: ERROR: UNKNOWN NUMBER OF FREE THROWS', idx)
            # print('CURRENT IDX: ' + str(idx))
            # print('CURRENT O-BOARD IDX: ' + str(o_board_index))
            # print(play_by_play_df.loc[idx - 10 : idx + 10][:])
            free_throws = 0
        
        # Determine how many free throws were made
        while free_throws > 0: 
            if (idx + counter >= len(play_by_play_df.index) - 1 
                and 'miss' not in str(play_by_play_df.loc[idx + counter][team1]).lower()): # If index out of range and free throw made, break loop and credit FT
                points_on_board += 1
                free_throws -= 1
                break
            elif (idx + counter >= len(play_by_play_df.index) - 1  
                  and 'miss' in str(play_by_play_df.loc[idx + counter][team1]).lower()): # If free throw missed, no credit to FT, move to next FT
                free_throws -= 1
                break
            elif 'miss' not in str(play_by_play_df.loc[idx + counter][team1]).lower(): # If free throw made, credit FT, move to next FT
                points_on_board += 1
                free_throws -= 1
                counter += 1
            else:
                free_throws -= 1
                counter += 1

        # Determine if there were any offensive rebounds on the same possession, before the FT 
        while True:
            if (idx <= 0 
                or (idx - o_board_index) <= 0
                or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5 
                or (play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1 
                and play_by_play_df.loc[idx - o_board_index][team1] == None)): #If there is a turnover or a made shot by the other team, break the loop
                break

            elif (idx <= 0
                 or (idx - o_board_index) <= 0
                 or ('miss' in str(play_by_play_df.loc[idx - o_board_index - 1][team2]).lower()
                 and play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 4)): # If there is a defensive rebound by the winning team, break the loop
                break

            elif (play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3
                 and play_by_play_df.loc[idx - o_board_index][team1] == None): # If the losing team takes a free throw break the loop
                break

            elif ('miss' in str(play_by_play_df.loc[idx - o_board_index - 1][team1]).lower()
                 and play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 4): # If there is a miss by the winning team and a subsequent rebound, add to the oreb sequence and continue the loop
                oreb_sequence += 1
                o_board_index += 1

            elif (play_by_play_df.loc[idx - o_board_index - 1]['EVENTMSGTYPE'] == 3 
                 and 'miss' in str(play_by_play_df.loc[idx - o_board_index - 1][team1]).lower()
                 and play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 4): # If your team missed a free throw and grabbed the rebound add to the oreb sequence and continue the loop
                oreb_sequence += 1
                o_board_index += 1

            else: # Keep cycling through all other irrelevant events
                o_board_index += 1
        
        # Assign value to FT shooter based on how many free throws they hit, the other factors in the possession
        
        if points_on_board < offense_possession_value: #If the player missed enough free throws to lose value on the possession, dock them the entire loss of value
            # print('Free Throw Event: ' + str(idx))
            # print('points on board: ' + str(points_on_board))
            # print('points on board: ' + str(offense_possession_value))
            current_player_ft_negative += (points_on_board - offense_possession_value)
        
        else: #If positive value was gain on the posession, assign the value based on the value structure listed above
            if ast == 1 and oreb_sequence > 0:
                current_player_ft_positive += (points_on_board - offense_possession_value) * Assissted_FT_After_OREB
            elif ast == 1 and oreb_sequence == 0:
                current_player_ft_positive += (points_on_board - offense_possession_value) * Assisted_FT
            elif ast == 0 and oreb_sequence > 0:
                current_player_ft_positive += (points_on_board - offense_possession_value) * FT_After_OREB
            else:
                current_player_ft_positive += points_on_board - offense_possession_value
            
        
    return [current_player_ft_positive, current_player_ft_negative] 
    