import pandas as pd

# Blocks Value Structure

block_before_turnover = .5
block_with_rebound = .9
defense_value = 2.2 # Possession value can be subtracted by this for an alternate way of evaluating. This makes the assumption that blocking something is stopping a field goal that is likely to go in, rather than just the expected value of a field goal

def score_blocks(game_df, general_df, current_player, home_away, team_id, defense_possession_value):
    current_player_blocks_score = 0 # Set blocks score to 0

    # Blocks works differently than other events because there is no explicit message type for it
    # We need to find strings within the game_df which contain the word 'block' and the name of the player being evaluated
    # Finding those events creates our player_events_df

    player_last_name = general_df['PLAYER_NAME'].where(general_df['PLAYER_ID'] == current_player).dropna().reset_index().drop(columns='index') 
    player_last_name = str(player_last_name).split()[-1]
    player_events_df = game_df[(game_df['WINNINGTEAM'].str.contains("BLOCK", na=False)) & (game_df['WINNINGTEAM'].str.contains(player_last_name, na=False))]

    # game_df and player_events_df have the same indexes
    # game_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # It is filtered to include events related to the current staistic, in this case blocks
    # Moving down game_df means looking at events which happened after the result being analyzed in the player_events_df
       # In regards to blocks, this means looking to see if the losing team scored after the block or if the winning team came up with a stop

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every block by this player
        shot_made_index = 1 # Called shot_made_index because we are looking to see if the losing team made a shot, which would make the block worthless
        while True:
            if idx + shot_made_index > len(game_df.index) - 1: # If we go to an index outside the game_df, there must be no score after the block
                current_player_blocks_score += defense_possession_value # Add score to player's blocks score using the value of a defensive possession
                break

            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 1
                  and game_df.loc[idx + shot_made_index]['WINNINGTEAM'] == None): # If we see that the loing team made a shot assign no value to the block and move onto the next block to be evaluated
                break

            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 4
                  and game_df.loc[idx + shot_made_index]['WINNINGTEAM'] != None): # If there is a rebound by the winning team, award value to the block and move onto next block
                current_player_blocks_score += defense_possession_value * block_with_rebound
                break
                
            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 5 
                 and 'steal' in str(game_df.loc[idx + shot_made_index]['WINNINGTEAM']).lower()): # If a steal caused a change in possession by the losing team, award the block value based on value structure with turnover
                current_player_blocks_score += defense_possession_value * block_before_turnover
                break

            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 5 
                 and game_df.loc[idx + shot_made_index]['WINNINGTEAM'] == None): # If there was a turnover that was not a steal, award 100% value for block
                current_player_blocks_score += defense_possession_value
                break

            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 2 
                  and (game_df.loc[idx + shot_made_index + 1]['EVENTMSGTYPE'] == 4 
                  and game_df.loc[idx + shot_made_index + 1]['LOSINGTEAM'] == None)): # If there was a missed shot followed by a rebound by the winning team
                if game_df.loc[idx + shot_made_index + 1]['PLAYER1_ID'] == None: # If the rebound was a team rebound, award the block 100% value
                    current_player_blocks_score += defense_possession_value
                    break

                else:
                    current_player_blocks_score += defense_possession_value * block_with_rebound # If the rebound wasn't a team rebound, award the block the percentage value associated with a defensive rebound
                    break

            elif (game_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 3 
                  and game_df.loc[idx + shot_made_index]['PLAYER1_TEAM_ID'] != team_id): # If there were free throws by the losing team after the block 
                counter = 0 # Total free throws counter
                points_off_board = 0 # Free throw made counter
                if 'technial' in str(game_df.loc[idx + shot_made_index]['LOSINGTEAM']).lower(): # If free throws caused by technical foul
                    free_throws = 1
                    if 'pts' in str(game_df.loc[idx + shot_made_index + counter]['LOSINGTEAM']).lower(): # If tehnical free throw is made
                        points_off_board += 1 # Add points scored on the possession
                        free_throws -= 1
                        counter += 1
                    else: # If technical free throw is missed
                        free_throws -= 1
                        counter += 1
                elif 'of 1' in str(game_df.loc[idx + shot_made_index]['LOSINGTEAM']).lower(): # If there was 1 free throw
                    free_throws = 1
                elif 'of 2' in str(game_df.loc[idx + shot_made_index]['LOSINGTEAM']).lower(): # If there were 2 free throws
                    free_throws = 2
                elif 'of 3' in str(game_df.loc[idx + shot_made_index]['LOSINGTEAM']).lower(): # If there were 3 free throws
                    free_throws = 3
                else: # Print errors if there are an unknown number of free throws
                    print('BLOCK: ', str(game_df.loc[idx]['LOSINGTEAM']).lower())
                    print('BLOCK: ', str(game_df.loc[idx + shot_made_index]['LOSINGTEAM']).lower())
                    print('BLOCK: ERROR: UNKNOWN NUMBER OF FREE THROWS', idx)
                    free_throws = 0
                
                while free_throws > 0: # Continue going down the game_df if there are still free throw shots to be taken
                    if game_df.loc[idx + shot_made_index + counter]['EVENTMSGTYPE'] == 4: # There is a nuance that team rebounds are often included in between free throws. If there is a rebound in the free throw sequence, move to th next index
                        counter += 1
                        continue
                    elif 'miss' not in str(game_df.loc[idx + shot_made_index + counter]['LOSINGTEAM']).lower(): # If a free throw is made
                            points_off_board += 1 # Add to the points scored on the possession
                            free_throws -= 1 # Decrease amount of free throws left to take
                            counter += 1 # Increase the index to check (next free throw is the next index)
                    else: # If the player missed, decrease the free throws left to shoot
                        free_throws -= 1
                        counter += 1
                if (idx + shot_made_index + counter + 1 > len(game_df.index) - 1
                    or game_df.loc[idx + shot_made_index + counter + 1]['EVENTMSGTYPE'] == 4
                    and game_df.loc[idx + shot_made_index + counter]['WINNINGTEAM'] != None): # If there is a defensive rebound after the free throw, give credit to the block based on the amount of free throws made
                    if points_off_board > defense_possession_value: # Don't penalize player who got the block for free throws, but give them value if the free throw shooter doesn't make enough
                        break
                    else:
                        current_player_blocks_score += (defense_possession_value - points_off_board) * block_before_turnover
                    break

                else:
                    if points_off_board > defense_possession_value: # Don't penalize player who got the block for free throws, but give them value if the free throw shooter doesn't make enough
                        break
                    else:
                        current_player_blocks_score += (defense_possession_value - points_off_board) * block_before_turnover
                        break

            else:
                shot_made_index += 1 # Move down game_df one row

            
    if current_player_blocks_score is None:
        return 0
    else:
        
        return current_player_blocks_score # Return the blocks score for this player for this game