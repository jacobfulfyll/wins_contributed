import pandas as pd
import numpy as np
from Prep_Functions.game_possession_info import possession_variables
from Score_Possessional_Data.score_points import score_points
from Score_Possessional_Data.score_assists import score_assists
from Score_Possessional_Data.score_rebs import score_rebs
from Score_Possessional_Data.score_stls import score_stls
from Score_Possessional_Data.score_to import score_to
from Score_Possessional_Data.score_blocks import score_blocks
from Score_Possessional_Data.score_ft import score_ft
from Score_Possessional_Data.score_missed_fg import score_missed_fg
from Score_Possessional_Data.score_def_foul import score_def_foul

def one_game_wins(game_id, game_df, general_dfs, current_team_id, winning_team, losing_team):
    
    # Create dataframe for value box score
    final_df = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name','points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr'])

    win_loss = 2
    for general_df in general_dfs:
        # Create dataframe for current team value box score
        df = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id', 'player_name', 'points_score', 'assists_score', 'orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score', 'ft_score', 'dfg_score', 'sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score'])
        # Get possession variables
        win_loss -= 1 # win_loss inserts 1 for the winning team and 0 for the losing team
        offense_possession_value, defense_possession_value, effective_ft_pct = possession_variables(game_id, winning_team, losing_team, win_loss)
    
        if win_loss == 1:
            team_id = winning_team
            opponent_id = losing_team
        else:
            team_id = losing_team
            opponent_id = winning_team

        # Loop through every player on the current team
        for idx, player_id in general_df['PLAYER_ID'].iteritems():
            player_name = general_df.loc[idx]['PLAYER_NAME']
            player_events_df = game_df[(game_df['PLAYER1_ID'] == player_id) | (game_df['PLAYER2_ID'] == player_id)]
            
            # Score points for each player for current game
            if general_df.loc[idx]['FG2M'] != 0 or general_df.loc[idx]['FG3M'] != 0:
                points_score = score_points(player_events_df, game_df, player_id, win_loss, current_team_id, offense_possession_value) * general_df.loc[idx]['offense_factor2']
            else:
                points_score = 0

            # Score assists for each player for current game
            if general_df.loc[idx]['AST'] != 0:
                assists_score = score_assists(player_events_df, game_df, player_id, win_loss, current_team_id, offense_possession_value) * general_df.loc[idx]['offense_factor2']
            else:
                assists_score = 0
            
            # Score rebounds for each player for current game
            if general_df.loc[idx]['OREB'] != 0 or general_df.loc[idx]['DREB'] != 0:
                rebs_score = score_rebs(player_events_df, game_df, player_id, win_loss, current_team_id, offense_possession_value, defense_possession_value)
                rebs_score = list(rebs_score)
                rebs_score[1] = rebs_score[1] * general_df.loc[idx]['defense_factor2']
                rebs_score[0] = rebs_score[0] * general_df.loc[idx]['offense_factor2'] 
            else:
                rebs_score = [0, 0]
            
            # Score turnovers for each player for current game
            if general_df.loc[idx]['TO'] != 0:
                to_score = score_to(player_events_df, game_df, player_id, win_loss, current_team_id, offense_possession_value) * general_df.loc[idx]['offense_factor']
            else:
                to_score = 0

            # Score blocks for each player for current game
            if general_df.loc[idx]['BLK'] != 0:
                blocks_score = score_blocks(game_df, general_df, player_id, win_loss, current_team_id, defense_possession_value) * general_df.loc[idx]['defense_factor2']
            else:
                blocks_score = 0

            # Score FT for each player for current game
            if general_df.loc[idx]['FTA'] != 0:
                ft_score = score_ft(player_events_df, game_df, player_id, win_loss, current_team_id, offense_possession_value) * general_df.loc[idx]['offense_factor2']
            else:
                ft_score = 0

            # Score ft_ast for each player for current game
            if general_df.loc[idx]['FTAST'] != 0:
                ft_ast_score = general_df.loc[idx]['FTAST'] * ((2 * effective_ft_pct) - offense_possession_value) * .3 * general_df.loc[idx]['offense_factor2'] # .3 represents the value of an assist
            else:
                ft_ast_score = 0

            # Score steals for each player for current game
            if general_df.loc[idx]['STL'] != 0:
                stls_score = score_stls(player_events_df, game_df, player_id, win_loss, current_team_id, defense_possession_value) * general_df.loc[idx]['defense_factor2']
            else:
                stls_score = 0

            # Score missed field goals
            missed_fg_score = score_missed_fg(player_events_df, game_df, player_id, offense_possession_value, winning_team, win_loss) * general_df.loc[idx]['offense_factor']
            
            # Score defensive fouls
            def_fouls_score = score_def_foul(player_events_df, game_df, player_id, defense_possession_value, win_loss) * general_df.loc[idx]['defense_factor']

            # Score defended field goals
            dfg_score = general_df.loc[idx]['DFG'] * (defense_possession_value) * .8 * general_df.loc[idx]['defense_factor2']
            
            # Score screen assists
            sast_score = general_df.loc[idx]['SAST'] * (offense_possession_value) * .3 * general_df.loc[idx]['offense_factor2'] # Want to use what the offenses percentages are, which is called effective loss in this context. Need to negate it because a screen assist is positive unlike missed field goals or turnovers
            
            # Update df with player row
            df.loc[idx] = [game_id, win_loss, team_id, opponent_id, player_id, player_name, points_score, assists_score, rebs_score[0], rebs_score[1], to_score, stls_score, blocks_score, ft_score, dfg_score, sast_score, ft_ast_score, missed_fg_score, def_fouls_score]
    
        # Create sum column
        df['jacob_value'] = df.iloc[:, 4:].sum(axis=1)

        # Recalculate sum column with a 0 base - Negative value fix
        wins_list = np.empty(len(df['jacob_value']))
        for idx, event in df['jacob_value'].iteritems():
            wins_list[idx] = event - df['jacob_value'].min()

        # Playing time adjustment and final wins contributed calculation
        wins_sum = np.sum(wins_list)
        df['wins_contr'] = wins_list / wins_sum
        df['wins_contr'] = df['wins_contr'] * general_df['SEC_FACT']

        df['wins_contr'] = df['wins_contr'] / df['wins_contr'].sum(axis=0)

        final_df = final_df.append(df)
    
    return final_df[['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name','points_score','assists_score','orebs_score', 'drebs_score', 'to_score', 'stls_score', 'blocks_score','ft_score','dfg_score','sast_score', 'ft_ast_score', 'missed_fg_score', 'def_fouls_score', 'jacob_value', 'wins_contr']]