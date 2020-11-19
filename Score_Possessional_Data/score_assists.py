import pandas as pd
import pdb

# Assist Value Structure:

Assist = .3 # Assists receive 30% of value created from made shot when no offensive rebound
Assisted_After_OREB = .2 # Assists receive 20% of value created from made shot when after offensive rebound

# Run this function for every player who had an assist within a given game
def score_assists(player_events_df, play_by_play_df, current_player, win_loss, team_id, offense_possession_value):
    two_pointer_assists = 0
    three_pointer_assists = 0
    two_pointer_assists_after_orebs = 0
    three_pointer_assists_after_orebs = 0

    # Limit player_events_df to only assist related rows. EVENTMSGTYPE 1 = Made Shot
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 1) 
                       & (player_events_df['PLAYER2_ID'] == current_player)]

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'

    # play_by_play_df and player_events_df have the same indexes
    # play_by_play_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case assists
    # Moving up play_by_play_df means looking at events which happened before the result being analyzed in the player_events_df
       # In regards to assists, this means looking for offensive rebounds which happened previously within the same possession

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every assist by this player in this game

        o_board_index = 1
        while True:
            if idx == 0:
                o_board_index = 0
                break
            elif ((idx - o_board_index) == 0
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1 
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 2
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 3
            or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5): # Go up the chain until you find the last missed/made shot or free throw, because an offensive rebound can only happen on a missed shot or free throw
                break
            else: 
                o_board_index += 1 # Increasing o_board_index lets you keep moving up the events in play_by_play_df

        if play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 5 or play_by_play_df.loc[idx - o_board_index]['EVENTMSGTYPE'] == 1: # If there was a turnover or a made shot, there were no offensive rebounds on the possession
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                two_pointer_assists += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            else:
                three_pointer_assists += (3 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated

        elif (play_by_play_df.loc[idx - o_board_index][team1] == None 
        or 'miss' in str(play_by_play_df.loc[idx - o_board_index][team2]).lower()): # If the last missed shot was from the losing team, there was no offensive rebound on this possession
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                two_pointer_assists += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            else:
                three_pointer_assists += (3 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
        
        elif (play_by_play_df.loc[idx - o_board_index + 1]['EVENTMSGTYPE'] == 4
        and play_by_play_df.loc[idx - o_board_index + 1][team1] == None): # If the event following the previous change of possession is a defensive rebound by the other team, there was no offensive rebound before this assist
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                two_pointer_assists += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            else:
                three_pointer_assists += (3 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
        
        elif ('miss' in str(play_by_play_df.loc[idx - o_board_index][team1]).lower() 
        and play_by_play_df.loc[idx - o_board_index + 1]['EVENTMSGTYPE'] == 4
        and 'rebound' in str(play_by_play_df.loc[idx - o_board_index + 1][team1]).lower()): # If the last missed shot was rebounded by the winning team, there was an offensive rebound on the possession
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                two_pointer_assists_after_orebs += (2 - offense_possession_value) * Assisted_After_OREB # Add the value created on the possession, multiply by the offensive rebound with assit factor rather than the assist factor
            else:
                three_pointer_assists_after_orebs += (3 - offense_possession_value) * Assisted_After_OREB  # Add the value created on the possession, multiply by the offensive rebound with assit factor rather than the assist factor 
        
        else:
            # print('SCORING ASSISTS ERROR')
            # print('CURRENT IDX: ' + str(idx))
            # print('CURRENT O-BOARD IDX: ' + str(o_board_index))
            # print(play_by_play_df.loc[idx - 10 : idx + 10][:])
            #pdb.set_trace()
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                two_pointer_assists += (2 - offense_possession_value) * Assist # Add the value created on the possession, assigned to the assister to the current assist score for the player being evaluated
            else:
                three_pointer_assists += (3 - offense_possession_value) * Assist
        
    return [two_pointer_assists, three_pointer_assists, two_pointer_assists_after_orebs, three_pointer_assists_after_orebs]
