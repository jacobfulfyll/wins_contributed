import pandas as pd

block_before_foul = .5


def score_def_foul(player_events_df, game_df, current_player, defense_possession_value, win_loss):
    positive_def_fouls = 0
    negative_def_fouls = 0
    player_events_df = player_events_df[(player_events_df['EVENTMSGTYPE'] == 6) & (player_events_df['PLAYER1_ID'] == current_player)]
    
    if win_loss == 1:
        team1 = 'WINNINGTEAM'
        team2 = 'LOSINGTEAM'
    else:
        team1 = 'LOSINGTEAM'
        team2 = 'WINNINGTEAM'
   
    # game_df and player_events_df have the same indexes
    # game_df includes every play from the game 
    # player_events_df includes only events the current player being evaluated was involved in
    # player_events_df is filtered to include events related to the current staistic, in this case personal fouls

    for idx, event in player_events_df['EVENTMSGTYPE'].iteritems(): # For every personal foul committed by this player
        def_fouls_score = 0
        if idx + 1 > len(game_df.index) - 1: # If the next index is more than the max index in the df, break
            break

        elif game_df.loc[idx + 1]['EVENTMSGTYPE'] == 3: # If the next index is a free throw, we know it was a shooting foul
            counter = 0
            if 'of 1' in str(game_df.loc[idx + 1][team2]).lower(): # 1 shot free throw
                free_throws = 1
            elif 'of 2' in str(game_df.loc[idx + 1][team2]).lower(): # 2 shot free throw
                free_throws = 2
            elif 'of 3' in str(game_df.loc[idx + 1][team2]).lower(): # 3 shot free throw
                free_throws = 3
            else:
                free_throws = 0
            
            while free_throws > 0:
                if 'miss' not in str(game_df.loc[idx + 1 + counter][team2]).lower(): # If free throw is made
                    def_fouls_score -= 1 # Decrease player fouls score
                    free_throws -= 1 # Decrease free throws left
                    counter += 1 # Check next row
                else:
                    free_throws -= 1
                    counter += 1

        if -def_fouls_score < defense_possession_value:
            counter = 1
            while True:
                if idx == 0 or (idx - counter) == 0:          # If index = 0, there were no offensive rebounds before this assist
                    positive_def_fouls += (def_fouls_score + defense_possession_value)
                    break
                elif (game_df.loc[idx - counter]['EVENTMSGTYPE'] == 2 
                and 'block' in str(game_df.loc[idx - counter][team1]).lower()):
                    positive_def_fouls += (def_fouls_score + defense_possession_value) * block_before_foul
                    break
                elif (game_df.loc[idx - counter]['EVENTMSGTYPE'] == 5
                or game_df.loc[idx - counter]['EVENTMSGTYPE'] == 1
                or (game_df.loc[idx - counter]['EVENTMSGTYPE'] == 4 and game_df.loc[idx - counter][team2] == None)
                or (game_df.loc[idx - counter]['EVENTMSGTYPE'] == 2 and game_df.loc[idx - counter][team2] == None)): # If there is a turnover, a made basket, a rebound by the winning team, or a missed shot by the winning team
                    positive_def_fouls += (def_fouls_score + defense_possession_value)
                    break
                else:
                    counter += 1
        else:
            negative_def_fouls += def_fouls_score + defense_possession_value
        
    
    return [positive_def_fouls, negative_def_fouls] # Return def_fouls_score which is negative + the possession value for defense