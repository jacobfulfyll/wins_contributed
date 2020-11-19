import pandas as pd

# Run this function for every player who missed a field goal within a given game
def score_missed_fg (player_events_df, play_by_play_df, current_player, offense_possession_value, winning_team, win_loss):
    missed_2fg_score = 0
    missed_3fg_score = 0
    missed_2fg_maintained_possession = 0
    missed_3fg_maintained_possession = 0

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'

    # Limit player_events_df to only missed_fg related rows. EVENTMSGTYPE 2 = Missed FG
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 2) & (player_events_df['PLAYER1_ID'] == current_player)]

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): #For every missed shot for current player
        if ((play_by_play_df.loc[idx + 1]['EVENTMSGTYPE'] == 4
            and play_by_play_df.loc[idx + 1][team1] == None)
            or (play_by_play_df.loc[idx + 1]['EVENTMSGTYPE'] == 6 
            and play_by_play_df.loc[idx + 1][team2] == None) 
            or idx + 1 > len(play_by_play_df.index) - 1): # If there was a change in possession after the shot, dock points from shooter
            
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                missed_2fg_score += -offense_possession_value
            else:
                missed_3fg_score += -offense_possession_value
        
        else: # If there wasn't a change in possession as a result of the shot, don't dock points
            if '3pt' not in str(player_events_df.loc[idx][team1]).lower():
                missed_2fg_maintained_possession += 1
            else:
               missed_3fg_maintained_possession += 1

    return [missed_2fg_score, missed_3fg_score, missed_2fg_maintained_possession, missed_3fg_maintained_possession]


    '''

    Previous Calculuations

                continue
            elif ((play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 4 
                  and play_by_play_df.loc[idx + counter]['LOSINGTEAM'] == None)
                  or (play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 6
                  and play_by_play_df.loc[idx + counter]['WINNINGTEAM'] == None)): # If there was an offensive rebound or a foul after the shot
                while True:
                    if (idx + counter > len(play_by_play_df.index) - 1 
                       or (play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 4
                       and play_by_play_df.loc[idx + counter]['WINNINGTEAM'] == None)
                       or play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 5): # If there was a defensive rebound a turnover, dock points from shooter
                        current_player_missed_fg_score += -offense_possession_value
                        break
                    elif ((play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 4
                          or play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 2)
                          and play_by_play_df.loc[idx + counter]['LOSINGTEAM'] == None): # If there was an offensive rebound or another missed shot, move on
                        counter += 1
                        missed_shot = 1
                    elif ((play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 1
                          or play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 3)
                          and play_by_play_df.loc[idx + counter]['LOSINGTEAM'] == None): # If there was a made shot player who missed fg not docked points
                        break
                    else:
                        counter += 1
                break
            
            elif play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 2 and play_by_play_df.loc[idx + counter]['LOSINGTEAM'] == None:
                counter += 1
            
            elif (play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 1 or play_by_play_df.loc[idx + counter]['EVENTMSGTYPE'] == 3) and play_by_play_df.loc[idx + counter]['LOSINGTEAM'] == None:
                break

            else:
                counter += 1
'''