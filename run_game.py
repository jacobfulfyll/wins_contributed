import pandas as pd
import numpy as np
from Prep_Functions.possession_value import possession_value
from Score_Possessional_Data.score_points import score_points
from Score_Possessional_Data.score_assists import score_assists
from Score_Possessional_Data.score_rebs import score_rebs
from Score_Possessional_Data.score_stls import score_stls
from Score_Possessional_Data.score_to import score_to
from Score_Possessional_Data.score_blocks import score_blocks
from Score_Possessional_Data.score_ft import score_ft
from Score_Possessional_Data.score_missed_fg import score_missed_fg
from Score_Possessional_Data.score_def_foul import score_def_foul

def get_value_contributed_boxscore(game_id, play_by_play_df,  val_contr_inputs_df_list, winning_team, losing_team):
    
    # Create dataframe for value box score
    value_contributed_boxscore = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name','TWO_PT_SCORE_UAST', 'THREE_PT_SCORE_UAST', 'TWO_PT_SCORE_AST', 'THREE_PT_SCORE_AST', 'TWO_PT_SCORE_UAST_OREB', 'THREE_PT_SCORE_UAST_OREB', 'TWO_PT_SCORE_AST_OREB', 'THREE_PT_SCORE_AST_OREB', 'AST_2PT', 'AST_3PT', 'AST_TWO_PT_OREB', 'AST_THREE_PT_OREB', 'OREB_TWO_PT_UAST', 'OREB_TWO_PT_AST', 'OREB_THREE_PT_UAST', 'OREB_THREE_PT_AST', 'OREB_FT', 'DREB_BLK', 'DREB_NO_BLK', 'TO_SCORE', 'STLS_SCORE', 'BLKS_SCORE', 'POSITIVE_FT', 'NEGATIVE_FT', 'DFG_SCORE','SAST_SCORE', 'FT_AST_SCORE', 'MISSED_TWO_PT_FG', 'MISSED_THREE_PT_FG', 'POSITIVE_DEF_FOULS', 'NEGATIVE_DEF_FOULS','TOTAL_VALUE', 'NORMALIZED_VALUE', 'FACTORED_VALUE', 'VALUE_CONTRIBUTED'])
    play_by_play_adjustments_df = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name', 'OREBS_NO_SCORE', 'FAILED_BLKS', 'MISSED_TWO_PT_FG_POSSESSION', 'MISSED_THREE_PT_FG_POSSESSION'])

    win_loss = 2
    for val_contr_inputs_df in  val_contr_inputs_df_list:
        # Create dataframe for current team value box score
        df1 = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name', 'TWO_PT_SCORE_UAST', 'THREE_PT_SCORE_UAST', 'TWO_PT_SCORE_AST', 'THREE_PT_SCORE_AST', 'TWO_PT_SCORE_UAST_OREB', 'THREE_PT_SCORE_UAST_OREB', 'TWO_PT_SCORE_AST_OREB', 'THREE_PT_SCORE_AST_OREB', 'AST_2PT', 'AST_3PT', 'AST_TWO_PT_OREB', 'AST_THREE_PT_OREB', 'OREB_TWO_PT_UAST', 'OREB_TWO_PT_AST', 'OREB_THREE_PT_UAST', 'OREB_THREE_PT_AST', 'OREB_FT', 'DREB_BLK', 'DREB_NO_BLK', 'TO_SCORE', 'STLS_SCORE', 'BLKS_SCORE', 'POSITIVE_FT', 'NEGATIVE_FT', 'DFG_SCORE','SAST_SCORE', 'FT_AST_SCORE', 'MISSED_TWO_PT_FG', 'MISSED_THREE_PT_FG', 'POSITIVE_DEF_FOULS', 'NEGATIVE_DEF_FOULS'])
        df2 = pd.DataFrame(columns=['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name', 'OREBS_NO_SCORE', 'FAILED_BLKS', 'MISSED_TWO_PT_FG_POSSESSION', 'MISSED_THREE_PT_FG_POSSESSION'])
        # Get possession variables
        win_loss -= 1 # win_loss inserts 1 for the winning team and 0 for the losing team
        offense_possession_value, defense_possession_value, effective_ft_pct = possession_value(game_id, winning_team, losing_team, win_loss)
        # print('Team: ' + str(win_loss))
        # print('Possession Value: ' + str(offense_possession_value))
        if win_loss == 1:
            team_id = winning_team
            opponent_id = losing_team
        else:
            team_id = losing_team
            opponent_id = winning_team

        # Loop through every player on the current team
        for idx, player_id in val_contr_inputs_df['PLAYER_ID'].iteritems():
            player_name = val_contr_inputs_df.loc[idx]['PLAYER_NAME']
            player_events_df = play_by_play_df[(play_by_play_df['PLAYER1_ID'] == player_id) | (play_by_play_df['PLAYER2_ID'] == player_id)]
            #print('CURRENT PLAYER: ' + player_name)
            #print('TEAM_ID: ' + str(team_id))
            #print(player_events_df)
            # Score points for each player for current game
            #print('EVALUATING POINTS')
            if val_contr_inputs_df.loc[idx]['FG2_MADE'] != 0 or val_contr_inputs_df.loc[idx]['FG3_MADE'] != 0:
                points_list = score_points(player_events_df, play_by_play_df, player_id, win_loss, team_id, offense_possession_value)
                # print('POINTS LIST:')
                # print(points_list)
                points_list = [points_stat * val_contr_inputs_df.loc[idx]['offense_factor'] for points_stat in points_list]
            else:
                points_list = [0,0,0,0,0,0,0,0]
            #print('EVALUATING ASSISTS')
            # Score assists for each player for current game
            if val_contr_inputs_df.loc[idx]['AST'] != 0:
                assists_list = score_assists(player_events_df, play_by_play_df, player_id, win_loss, team_id, offense_possession_value)
                assists_list = [assists_stat * val_contr_inputs_df.loc[idx]['offense_factor'] for assists_stat in assists_list]
            else:
                assists_list = [0,0,0,0]
            #print('EVALUATING REBOUNDS')
            # Score rebounds for each player for current game
            if val_contr_inputs_df.loc[idx]['OREB'] != 0 or val_contr_inputs_df.loc[idx]['DREB'] != 0:
                orebs_list, drebs_list = score_rebs(player_events_df, play_by_play_df, player_id, win_loss, team_id, offense_possession_value, defense_possession_value)
                orebs_no_score = orebs_list[5]
                orebs_list = [orebs_stat * val_contr_inputs_df.loc[idx]['offense_factor'] for orebs_stat in orebs_list]
                orebs_list[5] = orebs_no_score
                drebs_list = [drebs_stat * val_contr_inputs_df.loc[idx]['defense_factor'] for drebs_stat in drebs_list]
            else:
                orebs_list = [0,0,0,0,0,0]
                drebs_list = [0,0]
            #print('EVALUATING TURNOVERS')
            # Score turnovers for each player for current game
            if val_contr_inputs_df.loc[idx]['TO'] != 0:
                to_score = score_to(player_events_df, play_by_play_df, player_id, win_loss, team_id, offense_possession_value) * (1 - (val_contr_inputs_df.loc[idx]['offense_factor'] - 1)) #Turnovers are less negative if the team was playing better with you on the floor and more negative if the reverse
            else:
                to_score = 0
            #print('EVALUATING BLOCKS')
            # Score blocks for each player for current game
            if val_contr_inputs_df.loc[idx]['BLK'] != 0:
                blocks_score, failed_blocks = score_blocks(play_by_play_df, val_contr_inputs_df, player_id, win_loss, team_id, defense_possession_value)
                blocks_score = blocks_score * val_contr_inputs_df.loc[idx]['defense_factor']
            else:
                blocks_score = 0
                failed_blocks = 0
            #print('EVALUATING FREE THROWS')
            # Score FT for each player for current game
            if val_contr_inputs_df.loc[idx]['FTA'] != 0:
                ft_list = score_ft(player_events_df, play_by_play_df, player_id, win_loss, team_id, offense_possession_value)
                ft_list[0] = ft_list[0] * val_contr_inputs_df.loc[idx]['offense_factor']
                ft_list[1] = ft_list[1] * (1 - (val_contr_inputs_df.loc[idx]['offense_factor'] - 1))
            else:
                ft_list = [0,0]
            #print('EVALUATING FREE THROW ASSISTS')
            # Score ft_ast for each player for current game
            if val_contr_inputs_df.loc[idx]['FTAST'] != 0:
                ft_ast_score = val_contr_inputs_df.loc[idx]['FTAST'] * ((2 * effective_ft_pct) - offense_possession_value) * .3 * val_contr_inputs_df.loc[idx]['offense_factor'] # .3 represents the value of an assist
            else:
                ft_ast_score = 0
            #print('EVALUATING STEALS')
            # Score steals for each player for current game
            if val_contr_inputs_df.loc[idx]['STL'] != 0:
                stls_score = score_stls(player_events_df, play_by_play_df, player_id, win_loss, team_id, defense_possession_value) * val_contr_inputs_df.loc[idx]['defense_factor']
            else:
                stls_score = 0
            #print('EVALUATING MISSED FG')
            # Score missed field goals
            if val_contr_inputs_df.loc[idx]['FG2_MISSED'] != 0 or val_contr_inputs_df.loc[idx]['FG3_MISSED'] != 0:
                missed_fg_list= score_missed_fg(player_events_df, play_by_play_df, player_id, offense_possession_value, winning_team, win_loss)
                maintained_possession_2pt = missed_fg_list[2]
                maintained_possession_3pt = missed_fg_list[3]
                missed_fg_list = [missed_fg_stat * (1 - (val_contr_inputs_df.loc[idx]['offense_factor'] - 1)) for missed_fg_stat in missed_fg_list]
                missed_fg_list[2] = maintained_possession_2pt
                missed_fg_list[3] = maintained_possession_3pt
            else:
                missed_fg_list = [0,0,0,0]
            #print('EVALUATING DEF FOULS')
            # Score defensive fouls
            def_fouls_list = score_def_foul(player_events_df, play_by_play_df, player_id, defense_possession_value, win_loss)
            def_fouls_list[0] = def_fouls_list[0] * val_contr_inputs_df.loc[idx]['defense_factor']
            def_fouls_list[1] = def_fouls_list[1] * (1 - (val_contr_inputs_df.loc[idx]['defense_factor'] - 1))

            # Score defended field goals
            dfg_score = val_contr_inputs_df.loc[idx]['DFG'] * (defense_possession_value) * .8 * val_contr_inputs_df.loc[idx]['defense_factor']
            
            # Score screen assists
            sast_score = val_contr_inputs_df.loc[idx]['SAST'] * (offense_possession_value) * .3 * val_contr_inputs_df.loc[idx]['offense_factor'] # Want to use what the offenses percentages are, which is called effective loss in this context. Need to negate it because a screen assist is positive unlike missed field goals or turnovers
            
            # Update df with player row
            df1.loc[idx] = [game_id, win_loss, team_id, opponent_id, player_id, player_name, points_list[0], points_list[1], points_list[2], points_list[3], points_list[4], points_list[5], points_list[6], points_list[7], assists_list[0], assists_list[1], assists_list[2], assists_list[3], orebs_list[0], orebs_list[1], orebs_list[2], orebs_list[3], orebs_list[4], drebs_list[0], drebs_list[1], to_score, stls_score, blocks_score, ft_list[0], ft_list[1], dfg_score, sast_score, ft_ast_score, missed_fg_list[0], missed_fg_list[1], def_fouls_list[0], def_fouls_list[1]]
            df2.loc[idx] = [game_id, win_loss, team_id, opponent_id, player_id, player_name, orebs_list[5], failed_blocks, missed_fg_list[2], missed_fg_list[3]]
        # Create sum column
        df1['TOTAL_VALUE'] = df1.iloc[:, 4:].sum(axis=1)
        df1['SEC_FACT'] = val_contr_inputs_df['SEC_FACT']
        # Recalculate sum column with a 0 base - Negative value fix
        df3 = df1[df1['SEC_FACT'] != 0].reset_index(drop=True)
        df4 = df1[df1['SEC_FACT'] == 0].reset_index(drop=True)

        value_list = np.empty(len(df3['TOTAL_VALUE']))
        for idx, event in df3['TOTAL_VALUE'].iteritems():
            if df3['TOTAL_VALUE'].min() < 0:
                value_list[idx] = event - df3['TOTAL_VALUE'].min()
            else:
                value_list[idx] = event

        # Playing time adjustment and final value contributed calculation
        #value_sum = np.sum(value_list)
        df3['NORMALIZED_VALUE'] = value_list #/ value_sum
        df3['FACTORED_VALUE'] = df3['NORMALIZED_VALUE'] * val_contr_inputs_df[val_contr_inputs_df['SEC_FACT'] != 0]['SEC_FACT'].reset_index(drop=True)

        df3['VALUE_CONTRIBUTED'] = df3['FACTORED_VALUE'] / df3['FACTORED_VALUE'].sum(axis=0)
        
        df4['VALUE_CONTRIBUTED'] = 0
        df4['NORMALIZED_VALUE'] = 0
        df4['FACTORED_VALUE'] = 0

        value_contributed_boxscore = value_contributed_boxscore.append(df3)
        value_contributed_boxscore = value_contributed_boxscore.append(df4)
        value_contributed_boxscore = value_contributed_boxscore[['game_id', 'win_loss', 'team_id', 'opponent_id', 'player_id','player_name','TWO_PT_SCORE_UAST', 'THREE_PT_SCORE_UAST', 'TWO_PT_SCORE_AST', 'THREE_PT_SCORE_AST', 'TWO_PT_SCORE_UAST_OREB', 'THREE_PT_SCORE_UAST_OREB', 'TWO_PT_SCORE_AST_OREB', 'THREE_PT_SCORE_AST_OREB', 'AST_2PT', 'AST_3PT', 'AST_TWO_PT_OREB', 'AST_THREE_PT_OREB', 'OREB_TWO_PT_UAST', 'OREB_TWO_PT_AST', 'OREB_THREE_PT_UAST', 'OREB_THREE_PT_AST', 'OREB_FT', 'DREB_BLK', 'DREB_NO_BLK', 'TO_SCORE', 'STLS_SCORE', 'BLKS_SCORE', 'POSITIVE_FT', 'NEGATIVE_FT', 'DFG_SCORE','SAST_SCORE', 'FT_AST_SCORE', 'MISSED_TWO_PT_FG', 'MISSED_THREE_PT_FG', 'POSITIVE_DEF_FOULS', 'NEGATIVE_DEF_FOULS','TOTAL_VALUE', 'NORMALIZED_VALUE', 'FACTORED_VALUE', 'VALUE_CONTRIBUTED']].reset_index(drop=True)
        play_by_play_adjustments_df = play_by_play_adjustments_df.append(df2)

        # consolidated_value_contributed_df1 = pd.DataFrame(columns=['player_name','FG_Made', 'FG_Missed', 'FT', 'AST', 'TO', 'OREB', 'DREB', 'STLS', 'BLKS', 'DFG', 'DEF_FOULS'])
        # consolidated_value_contributed_df1['player_name'] = value_contributed_boxscore['player_name']
        # consolidated_value_contributed_df1['FG_Made'] = value_contributed_boxscore['TWO_PT_SCORE_UAST'] + value_contributed_boxscore['THREE_PT_SCORE_UAST'] + value_contributed_boxscore['TWO_PT_SCORE_AST'] + value_contributed_boxscore['THREE_PT_SCORE_AST'] + value_contributed_boxscore['TWO_PT_SCORE_UAST_OREB'] + value_contributed_boxscore['THREE_PT_SCORE_UAST_OREB'] + value_contributed_boxscore['TWO_PT_SCORE_AST_OREB'] + value_contributed_boxscore['THREE_PT_SCORE_AST_OREB']
        # consolidated_value_contributed_df1['FG_Missed'] = value_contributed_boxscore['MISSED_TWO_PT_FG'] + value_contributed_boxscore['MISSED_THREE_PT_FG']
        # consolidated_value_contributed_df1['FT'] = value_contributed_boxscore['POSITIVE_FT'] + value_contributed_boxscore['NEGATIVE_FT']
        # consolidated_value_contributed_df1['AST'] = value_contributed_boxscore['AST_2PT'] + value_contributed_boxscore['AST_3PT'] + value_contributed_boxscore['AST_TWO_PT_OREB'] + value_contributed_boxscore['AST_THREE_PT_OREB'] + value_contributed_boxscore['SAST_SCORE'] + value_contributed_boxscore['FT_AST_SCORE']
        # consolidated_value_contributed_df1['TO'] = value_contributed_boxscore['TO_SCORE']
        # consolidated_value_contributed_df1['OREB'] = value_contributed_boxscore['OREB_TWO_PT_UAST'] + value_contributed_boxscore['OREB_TWO_PT_AST'] + value_contributed_boxscore['OREB_THREE_PT_UAST'] + value_contributed_boxscore['OREB_THREE_PT_AST'] + value_contributed_boxscore['OREB_FT']
        # consolidated_value_contributed_df1['DREB'] = value_contributed_boxscore['DREB_BLK'] + value_contributed_boxscore['DREB_NO_BLK']
        # consolidated_value_contributed_df1['STLS'] = value_contributed_boxscore['STLS_SCORE']
        # consolidated_value_contributed_df1['BLKS'] = value_contributed_boxscore['BLKS_SCORE']
        # consolidated_value_contributed_df1['DFG'] = value_contributed_boxscore['DFG_SCORE']
        # consolidated_value_contributed_df1['DEF_FOULS'] = value_contributed_boxscore['POSITIVE_DEF_FOULS'] + value_contributed_boxscore['NEGATIVE_DEF_FOULS']
        # consolidated_value_contributed_df1['TOTAL_VALUE'] = consolidated_value_contributed_df1.sum(axis=1)
        
        # consolidated_value_contributed_df2 = pd.DataFrame(columns=['player_name','FG2_Made', 'FG3_Made','FG2_Missed', 'FG3_Missed', 'POSITIVE_FT', 'NEGATIVE_FT', 'AST_2PT', 'AST_3PT', 'SAST', 'FT_AST', 'TO', 'OREB_2PT', 'OREB_3PT', 'OREB_FT', 'DREB_BLK', 'DREB_NO_BLK', 'STLS', 'BLKS', 'DFG', 'POSITIVE_DEF_FOULS', 'NEGATIVE_DEF_FOULS'])
        # consolidated_value_contributed_df2['player_name'] = value_contributed_boxscore['player_name']
        # consolidated_value_contributed_df2['FG2_Made'] = value_contributed_boxscore['TWO_PT_SCORE_UAST'] + value_contributed_boxscore['TWO_PT_SCORE_AST'] + value_contributed_boxscore['TWO_PT_SCORE_UAST_OREB'] + value_contributed_boxscore['TWO_PT_SCORE_AST_OREB']
        # consolidated_value_contributed_df2['FG3_Made'] = value_contributed_boxscore['THREE_PT_SCORE_UAST'] + value_contributed_boxscore['THREE_PT_SCORE_AST'] + value_contributed_boxscore['THREE_PT_SCORE_UAST_OREB'] + value_contributed_boxscore['THREE_PT_SCORE_AST_OREB']
        # consolidated_value_contributed_df2['FG2_Missed'] = value_contributed_boxscore['MISSED_TWO_PT_FG']
        # consolidated_value_contributed_df2['FG3_Missed'] = value_contributed_boxscore['MISSED_THREE_PT_FG']
        # consolidated_value_contributed_df2['POSITIVE_FT'] = value_contributed_boxscore['POSITIVE_FT']
        # consolidated_value_contributed_df2['NEGATIVE_FT'] = value_contributed_boxscore['NEGATIVE_FT']
        # consolidated_value_contributed_df2['AST_2PT'] = value_contributed_boxscore['AST_2PT'] + value_contributed_boxscore['AST_TWO_PT_OREB']
        # consolidated_value_contributed_df2['AST_3PT'] = value_contributed_boxscore['AST_3PT'] + value_contributed_boxscore['AST_THREE_PT_OREB']
        # consolidated_value_contributed_df2['SAST'] = value_contributed_boxscore['SAST_SCORE']
        # consolidated_value_contributed_df2['FT_AST'] = value_contributed_boxscore['FT_AST_SCORE']
        # consolidated_value_contributed_df2['TO'] = value_contributed_boxscore['TO_SCORE']
        # consolidated_value_contributed_df2['OREB_2PT'] = value_contributed_boxscore['OREB_TWO_PT_UAST'] + value_contributed_boxscore['OREB_TWO_PT_AST']
        # consolidated_value_contributed_df2['OREB_3PT'] = value_contributed_boxscore['OREB_THREE_PT_UAST'] + value_contributed_boxscore['OREB_THREE_PT_AST']
        # consolidated_value_contributed_df2['OREB_FT'] = value_contributed_boxscore['OREB_FT']
        # consolidated_value_contributed_df2['DREB_BLK'] = value_contributed_boxscore['DREB_BLK']
        # consolidated_value_contributed_df2['DREB_NO_BLK'] = value_contributed_boxscore['DREB_NO_BLK']
        # consolidated_value_contributed_df2['STLS'] = value_contributed_boxscore['STLS_SCORE']
        # consolidated_value_contributed_df2['BLKS'] = value_contributed_boxscore['BLKS_SCORE']
        # consolidated_value_contributed_df2['DFG'] = value_contributed_boxscore['DFG_SCORE']
        # consolidated_value_contributed_df2['POSITIVE_DEF_FOULS'] = value_contributed_boxscore['POSITIVE_DEF_FOULS']
        # consolidated_value_contributed_df2['NEGATIVE_DEF_FOULS'] = value_contributed_boxscore['NEGATIVE_DEF_FOULS']
        # consolidated_value_contributed_df2['TOTAL_VALUE'] = consolidated_value_contributed_df2.sum(axis=1)

        # print(consolidated_value_contributed_df1)
        # print(consolidated_value_contributed_df2)

    return value_contributed_boxscore, play_by_play_adjustments_df