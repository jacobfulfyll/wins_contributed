import pandas as pd
import pdb

#Rebounding Value Structure

OREB_Before_Assist = .4
OREB = .5
DREB = .2
DREB_After_Block = .1

# Run this function for every player who had a rebound within a given game
def score_rebs(player_events_df, play_by_play_df, current_player, win_loss, team_id, offense_possession_value, defense_possession_value):
    orebs_before_unassisted_two_pointer = 0
    orebs_before_assisted_two_pointer = 0
    orebs_before_unassisted_three_pointer = 0
    orebs_before_assisted_three_pointer = 0
    orebs_before_free_throws = 0
    orebs_no_score = 0
    drebs_after_block = 0
    drebs_no_block = 0

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'
    
    # Limit player_events_df to only rebound related rows. EVENTMSGTYPE 4 = Rebound
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 4) & (player_events_df['PLAYER1_ID'] == current_player)]
    
    # Create two dataframe, one for offensive rebounds, one for defensive rebounds
    oreb = pd.DataFrame(columns=['EVENTNUM', 'EVENTMSGTYPE', team1, 'NEUTRALDESCRIPTION',
       team2, 'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER2_ID',
       'PLAYER2_NAME', 'PLAYER3_ID', 'PLAYER3_NAME'])
    dreb = pd.DataFrame(columns=['EVENTNUM', 'EVENTMSGTYPE', team1, 'NEUTRALDESCRIPTION',
       team2, 'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER2_ID',
       'PLAYER2_NAME', 'PLAYER3_ID', 'PLAYER3_NAME'])

    # Populate dataframes with appropriate rebound types
    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems():
        if 'miss' in str(play_by_play_df.loc[idx - 1][team1]).lower():
            oreb = oreb.append(player_events_df.loc[idx][:])
        elif 'miss' in str(play_by_play_df.loc[idx - 1][team2]).lower():
            dreb = dreb.append(player_events_df.loc[idx][:])     
        else:
            print('What Type Of Rebound Was This?') #So Far It Is back to back rebounds with no missed shot in between
            print('CURRENT IDX: ' + str(idx))
            #pdb.set_trace()
            print(play_by_play_df.loc[idx - 10 : idx + 10][:])
            oreb = oreb.append(player_events_df.loc[idx][:])
        
    for idx, event in oreb['EVENTMSGTYPE'].iteritems(): # For every o-reb
        o_board_index = 2 # need to look two rows above, because rebounding is always preceded by a shot
        shot_made_index = 1
        shot_not_made = 0
        oreb_sequence = 1
        points_on_board = 0
        two_pointer_check = 0
        three_pointer_check = 0
        free_throws_check = 0
        while True:
            if (idx + shot_made_index > len(play_by_play_df.index) - 1 # Going passed the last index
            or play_by_play_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 5 # Turnover
            or ('miss' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower() and play_by_play_df.loc[idx + shot_made_index + 1]['EVENTMSGTYPE'] == 4 and play_by_play_df.loc[idx + shot_made_index + 1][team2] != None)): # Missed shot rebounded by the losing team
                shot_not_made = 1 # No shot was made following the offensive rebound
                orebs_no_score += 1
                break
                
            elif (play_by_play_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 1 # Made Shot Check
            and play_by_play_df.loc[idx + shot_made_index]['PLAYER1_TEAM_ID'] == team_id): # Correct Team Check
                if '3pt' not in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): 
                    points_on_board = 2 # Made two pointer
                    two_pointer_check = 1
                    break
                else:
                    points_on_board = 3 # Made three pointer
                    three_pointer_check = 1
                    break
            elif (play_by_play_df.loc[idx + shot_made_index]['EVENTMSGTYPE'] == 3 # Free Throws Check
            and play_by_play_df.loc[idx + shot_made_index]['PLAYER1_TEAM_ID'] == team_id): # Correct Team Check
                counter = 0
                free_throws_check = 1
                if 'technical' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): # If free throws caused by technical foul
                    free_throws = 0
                    if 'pts' in str(play_by_play_df.loc[idx + shot_made_index + counter][team1]).lower(): # If tehnical free throw is made
                        bonus_free_throw = 1 # Add points scored on the possession
                    else: # If technical free throw is missed
                        bonus_free_throw = 0
                elif 'of 1' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): # Amount of FT check
                    free_throws = 0
                    if 'miss' not in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower():
                        bonus_free_throw = 1 
                    else:
                        bonus_free_throw = 0
                elif 'of 2' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): # Amount of FT check
                    free_throws = 2
                elif 'of 3' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): # Amount of FT check
                    free_throws = 3
                else:
                    # print('O-REBS: ', str(play_by_play_df.loc[idx][team1]).lower())
                    # print('O-REBS: ', str(play_by_play_df.loc[idx + shot_made_index][team1]).lower())
                    # print('O-REBS: ERROR: UNKNOWN NUMBER OF FREE THROWS', idx)
                    # print('O-REBS SHOT INDEX: ' + str(shot_made_index))
                    # #pdb.set_trace()
                    # print(play_by_play_df.loc[idx - 10 : idx + 10][:])
                    free_throws = 1
                    #break
                
                while free_throws > 0:
                    if 'miss' not in str(play_by_play_df.loc[idx + shot_made_index + counter][team1]).lower():
                        points_on_board += 1 # Made Free Throw
                        free_throws -= 1
                        counter += 1 # Move on to next free throuw
                    else:
                        free_throws -= 1 # Missed Free Throw
                        counter += 1
                break
            elif ('miss' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower() # Missed Shot by Winning Team
            and play_by_play_df.loc[idx + shot_made_index + 1]['EVENTMSGTYPE'] == 4 # Rebound Following Missed Shot
            and play_by_play_df.loc[idx + shot_made_index + 1][team1] != None): # Winning Team Offensive Rebound
                oreb_sequence += 1 # Add Offensive Rebound which occurred later in the possession. This may still lead to another offensive rebound or a missed shot, in which case none of these rebounds are rewarded
                shot_made_index += 1 # Keep looking for next made shot or change in possession
            else:
                shot_made_index += 1 # Keep looking for next made shot or change in possession
                
        if shot_not_made == 1:
            continue
        else:
            while True:
                if (idx == 0 #If there is an index error, a turnover, or a made shot by the other team, break the loop
                or (idx - o_board_index) <= 0
                or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5
                or (play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1 and play_by_play_df.loc[idx - o_board_index][team1] == None)): 
                    break
                elif ('miss' in str(play_by_play_df.loc[idx - o_board_index - 1][team2]).lower()
                and play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 4): # If there is a defensive rebound by the winning team, break the loop
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
            if points_on_board < offense_possession_value: #Don't penalize offensive rebounder if free throw shooter missed shots
                continue
            elif 'ast' in str(play_by_play_df.loc[idx + shot_made_index][team1]).lower(): # If basket was assisted
                
                if two_pointer_check == 1:
                    orebs_before_assisted_two_pointer += (points_on_board - offense_possession_value) * (OREB_Before_Assist / oreb_sequence)
                elif three_pointer_check == 1:
                    orebs_before_assisted_three_pointer += (points_on_board - offense_possession_value) * (OREB_Before_Assist / oreb_sequence)
                else:
                    print('Assisted Make after Rebound With No TWO, THREE OR FREE THROWS Following')
            else:
                if two_pointer_check == 1:
                    orebs_before_unassisted_two_pointer += (points_on_board - offense_possession_value) * (OREB / oreb_sequence)
                elif three_pointer_check == 1:
                    orebs_before_unassisted_three_pointer += (points_on_board - offense_possession_value) * (OREB / oreb_sequence)
                elif free_throws_check == 1:
                    orebs_before_free_throws += (points_on_board - offense_possession_value) * (OREB / oreb_sequence)
                elif bonus_free_throw == 1:
                    orebs_before_free_throws += 1 * (OREB / oreb_sequence)
                else:
                    print('Unassisted Make after Rebound With No TWO, THREE OR FREE THROWS Following')
    

    for idx, event in dreb['EVENTMSGTYPE'].iteritems(): # For every d-reb
        counter = 1
        while True:
            if (idx == 0 # If previous row was one of these things, there was a change of possession
            or (idx - counter) <= 0 #Index out of scope
            or play_by_play_df.loc[idx - counter]['EVENTMSGTYPE'] == 5 # Turnover
            or play_by_play_df.loc[idx - counter]['EVENTMSGTYPE'] == 1): # Made shot
                drebs_no_block += defense_possession_value * DREB
                break

            elif (play_by_play_df.loc[idx - counter]['EVENTMSGTYPE'] == 2 # If there was a missed shot by the current team, there was a change of possession
            and play_by_play_df.loc[idx - counter][team1] != None):
                drebs_no_block += defense_possession_value * DREB
                break

            elif 'block' in str(play_by_play_df.loc[idx - counter][team1]).lower(): # If there was a block before a change of possession
                drebs_after_block += defense_possession_value * DREB_After_Block
                break

            else:
                counter += 1 #Cycle through rows
    
    return [orebs_before_unassisted_two_pointer, orebs_before_assisted_two_pointer, 
            orebs_before_unassisted_three_pointer, orebs_before_assisted_three_pointer, orebs_before_free_throws,
            orebs_no_score], [drebs_after_block, drebs_no_block]
