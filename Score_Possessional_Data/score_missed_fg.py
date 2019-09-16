import pandas as pd

# Run this function for every player who missed a field goal within a given game
def score_missed_fg (player_events_df, game_df, current_player, offense_possession_value, winning_team, win_loss):
    current_player_missed_fg_score = 0

    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'

    # Limit player_events_df to only missed_fg related rows. EVENTMSGTYPE 2 = Missed FG
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 2) & (player_events_df['PLAYER1_ID'] == current_player)]

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): #For every missed shot for current player
        if ((game_df.loc[idx + 1]['EVENTMSGTYPE'] == 4
            and game_df.loc[idx + 1][team1] == None)
            or (game_df.loc[idx + 1]['EVENTMSGTYPE'] == 6 
            and game_df.loc[idx + 1][team2] == None) 
            or idx + 1 > len(game_df.index) - 1): # If there was a change in possession after the shot, dock points from shooter
            current_player_missed_fg_score += -offense_possession_value
            continue
        
        else: # If there wasn't a change in possession as a result of the shot, don't dock points
            continue
    return current_player_missed_fg_score


    '''

    Previous Calculuations

                continue
            elif ((game_df.loc[idx + counter]['EVENTMSGTYPE'] == 4 
                  and game_df.loc[idx + counter]['LOSINGTEAM'] == None)
                  or (game_df.loc[idx + counter]['EVENTMSGTYPE'] == 6
                  and game_df.loc[idx + counter]['WINNINGTEAM'] == None)): # If there was an offensive rebound or a foul after the shot
                while True:
                    if (idx + counter > len(game_df.index) - 1 
                       or (game_df.loc[idx + counter]['EVENTMSGTYPE'] == 4
                       and game_df.loc[idx + counter]['WINNINGTEAM'] == None)
                       or game_df.loc[idx + counter]['EVENTMSGTYPE'] == 5): # If there was a defensive rebound a turnover, dock points from shooter
                        current_player_missed_fg_score += -offense_possession_value
                        break
                    elif ((game_df.loc[idx + counter]['EVENTMSGTYPE'] == 4
                          or game_df.loc[idx + counter]['EVENTMSGTYPE'] == 2)
                          and game_df.loc[idx + counter]['LOSINGTEAM'] == None): # If there was an offensive rebound or another missed shot, move on
                        counter += 1
                        missed_shot = 1
                    elif ((game_df.loc[idx + counter]['EVENTMSGTYPE'] == 1
                          or game_df.loc[idx + counter]['EVENTMSGTYPE'] == 3)
                          and game_df.loc[idx + counter]['LOSINGTEAM'] == None): # If there was a made shot player who missed fg not docked points
                        break
                    else:
                        counter += 1
                break
            
            elif game_df.loc[idx + counter]['EVENTMSGTYPE'] == 2 and game_df.loc[idx + counter]['LOSINGTEAM'] == None:
                counter += 1
            
            elif (game_df.loc[idx + counter]['EVENTMSGTYPE'] == 1 or game_df.loc[idx + counter]['EVENTMSGTYPE'] == 3) and game_df.loc[idx + counter]['LOSINGTEAM'] == None:
                break

            else:
                counter += 1
'''