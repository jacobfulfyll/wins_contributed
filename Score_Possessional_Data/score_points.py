import pandas as pd
import pdb

# Made Field Goals Value Structure
Assisted_FG = .7
Assisted_FG_After_OREB = .4
FG_After_OREB = .5

def add_to_score(event_string, offense_possession_value, current_scores_list, offensive_rebound=0):
    if offensive_rebound == 0:
        if 'ast' not in event_string: # If the shot was unassisted
            if '3pt' not in event_string: # If the shot was not a 3 pointer
                current_scores_list[0] += 2 - offense_possession_value
            else:
                current_scores_list[1] += 3 - offense_possession_value
               
        else:
            if '3pt' not in event_string: #If the shot was assisted 2 pointer
                current_scores_list[2] += (2 - offense_possession_value) * Assisted_FG
            else:
                current_scores_list[3] += (3 - offense_possession_value) * Assisted_FG
    else:
        if 'ast' not in event_string: # If the shot was unassisted
            if '3pt' not in event_string: # If the shot was not a 3 pointer
                current_scores_list[4] += (2 - offense_possession_value) * FG_After_OREB
            else:
                current_scores_list[5] += (3 - offense_possession_value) * FG_After_OREB
               
        else:
            if '3pt' not in event_string: #If the shot was assisted 2 pointer
                current_scores_list[6] += (2 - offense_possession_value) * Assisted_FG_After_OREB
            else:
                current_scores_list[7] += (3 - offense_possession_value) * Assisted_FG_After_OREB

    return current_scores_list



# Run this function for every player who made a field goal
def score_points(player_events_df, play_by_play_df, current_player, win_loss, team_id, offense_possession_value):
    unassisted_two_pointer_score = 0
    unassisted_three_pointer_score = 0
    assisted_two_pointer_score = 0
    assisted_three_pointer_score = 0
    unassisted_two_pointer_after_oreb_score = 0
    unassisted_three_pointer_after_oreb_score = 0
    assisted_two_pointer_after_oreb_score = 0
    assisted_three_pointer_after_oreb_score = 0
    current_scores_list = [unassisted_two_pointer_score, unassisted_three_pointer_score, assisted_two_pointer_score, 
                            assisted_three_pointer_score, unassisted_two_pointer_after_oreb_score, unassisted_three_pointer_after_oreb_score,
                            assisted_two_pointer_after_oreb_score, assisted_three_pointer_after_oreb_score]

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'

    # Limit player_events_df to only made_fg related rows. EVENTMSGTYPE 1 = Made Shot
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 1) & (player_events_df['PLAYER1_ID'] == current_player)]
    ##print(player_events_df)
    # play_by_play_df and player_events_df have the same index
    # play_by_play_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case made field goals
    # Moving up play_by_play_df means looking at events which happened before the result being analyzed in the player_events_df
       # In regards to points, this means looking for offensive rebounds which happened previously within the same possession

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every made field goal by this player
        o_board_index = 1
        while True:
            if idx == 0:
                o_board_index = 0
                break
            elif ((idx - o_board_index) == 0 
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1 
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 2 
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5): # Find the row with the last made shot, missed shot, or turnover
                break
            else: 
                o_board_index += 1
        if play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5 or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1: # If there was a turnover or a made shot, there were no offensive rebounds on the possession           
            current_scores_list = add_to_score(str(player_events_df.loc[idx][team1]).lower(), offense_possession_value, current_scores_list, offensive_rebound=0)
            

        if (play_by_play_df.loc[idx - o_board_index][team1] == None 
        or 'miss' in str(play_by_play_df.loc[idx - o_board_index][team2]).lower()): # If the row with the last missed shot was from the losing team, there were no offensive rebounds         
            current_scores_list = add_to_score(str(player_events_df.loc[idx][team1]).lower(), offense_possession_value, current_scores_list, offensive_rebound=0)
        
        
        elif ('miss' in str(play_by_play_df.loc[idx - o_board_index][team1]).lower() 
        and play_by_play_df.loc[idx - o_board_index + 1]['EVENTMSGTYPE'] == 4 
        and 'rebound' in str(play_by_play_df.loc[idx - o_board_index + 1][team1]).lower()): # If the last shot missed was from the winning team and was followed by a rebound, there was an offensive rebound in the possession              
            current_scores_list = add_to_score(str(player_events_df.loc[idx][team1]).lower(), offense_possession_value, current_scores_list, offensive_rebound=1)
        
                        
        else:
            # print('SCORING POINTS ERROR')
            # print('CURRENT IDX: ' + str(idx))
            # print('CURRENT O-BOARD IDX: ' + str(o_board_index))
            # print(play_by_play_df.loc[idx - 10 : idx + 10][:])
            # pdb.set_trace()
            current_scores_list = add_to_score(str(player_events_df.loc[idx][team1]).lower(), offense_possession_value, current_scores_list, offensive_rebound=0)
        
    return current_scores_list