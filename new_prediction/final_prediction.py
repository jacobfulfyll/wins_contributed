import pandas as pd
from time import sleep
import psycopg2 as pg2
from sqlalchemy import create_engine


team_predictions_full = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/team_predictions_1000_2020.csv')
team_predictions_injured = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/team_predictions_injuries_1000_2020.csv')

player_predictions_full = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/player_predictions_1000_2020.csv')
player_predictions_injured = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/player_predictions_injuries_1000_2020.csv')

print(player_predictions_full)

team_predictions_full['team_id'] = [int(x.split('_')[0]) for x in team_predictions_full['team_season_id']]
team_predictions_injured['team_id'] = [int(x.split('_')[0]) for x in team_predictions_injured['team_season_id']]


# injury_only_list = [1610612747, 1610612751, 1610612764, 1610612763, 1610612740]
# injury_partly_list = [1610612754, 1610612744, 1610612757, 1610612746]

# full_only_predictions = team_predictions_full
# for team in (injury_only_list + injury_partly_list):
#     full_only_predictions = full_only_predictions[full_only_predictions['team_id'] != team]

# injury_only_predictions = team_predictions_injured
# # print(injury_only_predictions)
# # for team in injury_only_list:
# #     print(team)
# injury_only_predictions = injury_only_predictions[(injury_only_predictions['team_id'] == injury_only_list[0]) | (injury_only_predictions['team_id'] == injury_only_list[1]) | (injury_only_predictions['team_id'] == injury_only_list[2]) | (injury_only_predictions['team_id'] == injury_only_list[3]) | (injury_only_predictions['team_id'] == injury_only_list[4])]

# print(injury_only_predictions)
# final_predictions_df = full_only_predictions.append(injury_only_predictions)
# final_predictions_df = final_predictions_df.groupby(['team_season_id', 'team_id']).mean().drop(columns='Unnamed: 0')
# print(final_predictions_df.sort_values('final_wins', ascending=False))


grouped_full = team_predictions_full.groupby(['team_season_id', 'team_id']).mean().drop(columns='Unnamed: 0')
grouped_injured = team_predictions_injured.groupby(['team_season_id', 'team_id']).mean().drop(columns='Unnamed: 0')

print(grouped_full.sort_values('final_wins', ascending=False))
print(grouped_injured.sort_values('final_wins', ascending=False))

data = [['1610612737_2020', 1610612737, 2020, 26, 56],
        ['1610612738_2020', 1610612738, 2020, 53, 29],
        ['1610612751_2020', 1610612751, 2020, 42, 40],
        ['1610612766_2020', 1610612766, 2020, 25, 57],
        ['1610612741_2020', 1610612741, 2020, 30, 52],
        ['1610612739_2020', 1610612739, 2020, 24, 58],
        ['1610612742_2020', 1610612742, 2020, 36, 46],
        ['1610612743_2020', 1610612743, 2020, 55, 27],
        ['1610612765_2020', 1610612765, 2020, 37, 45],
        ['1610612744_2020', 1610612744, 2020, 53, 29],
        ['1610612745_2020', 1610612745, 2020, 60, 22],
        ['1610612754_2020', 1610612754, 2020, 36, 46],
        ['1610612746_2020', 1610612746, 2020, 56, 26],
        ['1610612747_2020', 1610612747, 2020, 51, 31],
        ['1610612763_2020', 1610612763, 2020, 23, 59],
        ['1610612748_2020', 1610612748, 2020, 39, 43],
        ['1610612749_2020', 1610612749, 2020, 60, 22],
        ['1610612750_2020', 1610612750, 2020, 32, 50],
        ['1610612740_2020', 1610612740, 2020, 34, 48],
        ['1610612752_2020', 1610612752, 2020, 25, 57],
        ['1610612760_2020', 1610612760, 2020, 43, 39],
        ['1610612753_2020', 1610612753, 2020, 39, 43],
        ['1610612755_2020', 1610612755, 2020, 53, 29],
        ['1610612756_2020', 1610612756, 2020, 26, 56],
        ['1610612757_2020', 1610612757, 2020, 43, 39],
        ['1610612758_2020', 1610612758, 2020, 39, 43],
        ['1610612759_2020', 1610612759, 2020, 51, 31],
        ['1610612761_2020', 1610612761, 2020, 55, 27],
        ['1610612762_2020', 1610612762, 2020, 54, 28],
        ['1610612764_2020', 1610612764, 2020, 30, 52]]

final_team_predictions_df = pd.DataFrame(data, columns=['team_season_id','team_id','season_end','projected_wins', 'projected_losses'])

print(final_team_predictions_df)
print(final_team_predictions_df['projected_wins'].sum())
print(final_team_predictions_df['projected_losses'].sum())


injury_partly_list = ['1610612754_2020', '1610612744_2020', '1610612757_2020', '1610612746_2020']
injury_partly_pct = [.5, .75, .75, .18]
injury_team_counter = 0
final_full_player_predictions_df = pd.DataFrame()
# final_injured_player_predictions_df = pd.DataFrame()
for idx, team in final_team_predictions_df['team_season_id'].iteritems():
    full_players = player_predictions_full[player_predictions_full['team_season_id'] == team].groupby(['player_name', 'player_season_id']).mean().reset_index().drop(columns='Unnamed: 0')
    final_wins = final_team_predictions_df.loc[idx, 'projected_wins']
    final_losses = final_team_predictions_df.loc[idx, 'projected_losses']
    # print(full_players)
    # sleep(100)
    if team in injury_partly_list:
        injured_pct = injury_partly_pct[injury_team_counter]
        injury_team_counter += 1

        full_players['adjusted_wc'] = full_players['wins_contr'] * (1 - injured_pct)
        full_players['adjusted_lc'] = full_players['wins_contr'] * injured_pct
        
        injured_players = player_predictions_injured[player_predictions_injured['team_season_id'] == team].groupby(['player_name', 'player_season_id']).mean().reset_index().drop(columns='Unnamed: 0')
        injured_players['adjusted_wc'] = injured_players['wins_contr'] * (1 - injured_pct)
        injured_players['adjusted_lc'] = injured_players['wins_contr'] * injured_pct

        final_df = full_players.merge(injured_players, on=[ 'player_name', 'player_season_id'], how='outer')
        final_df = final_df.fillna(0)

        final_df['wc'] = final_df['adjusted_wc_x'] + final_df['adjusted_wc_y']
        final_df['lc'] = final_df['adjusted_lc_x'] + final_df['adjusted_lc_y']
        final_df = final_df.sort_values('wc', ascending=False).reset_index(drop=True)
        wins_contr_list = []
        losses_contr_list = []
        for idx in range(len(final_df)):
            if idx <= 9:
                wins_contr_list.append((final_df.loc[idx, 'wc'] / final_df['wc'][0:11].sum()) * (final_wins * .99))
                losses_contr_list.append((final_df.loc[idx, 'lc'] / final_df['lc'][0:11].sum()) * (final_losses * .99))
            else:
                wins_contr_list.append((final_df.loc[idx, 'wc'] / final_df['wc'][11:].sum()) * (final_wins * .01))
                losses_contr_list.append((final_df.loc[idx, 'lc'] / final_df['lc'][11:].sum()) * (final_losses * .01)) 

        
        final_df['wins_contr'] = wins_contr_list
        final_df['losses_contr'] = losses_contr_list
        final_df['val_contr'] = final_df['wins_contr'] + final_df['losses_contr']
        final_df['difference'] = final_df['wins_contr'] - final_df['losses_contr']
        final_df['team_season_id'] = team

        final_df = final_df.drop(columns=['adjusted_wc_x', 'adjusted_wc_y', 'adjusted_lc_x', 'adjusted_lc_y', 'wc', 'lc', 'wins_contr_x',  'losses_contr_x',  'val_contr_x', 'difference_x',  'wins_contr_y',  'losses_contr_y',  'val_contr_y',  'difference_y'])
        #final_df = final_df[['player_name', 'player_season_id', 'wins_contr', 'losses_contr', 'val_contr', 'difference', 'team_season_id']]
        # print(final_df)
        final_full_player_predictions_df = final_full_player_predictions_df.append(final_df)
    else:
        full_players['team_season_id'] = team
        full_players = full_players.sort_values('wins_contr', ascending=False).reset_index(drop=True)
        wins_contr_list = []
        losses_contr_list = []
        for idx in range(len(full_players)):
            if idx <= 9:
                wins_contr_list.append((full_players.loc[idx, 'wins_contr'] / full_players['wins_contr'][0:11].sum()) * (final_wins * .99))
                losses_contr_list.append((full_players.loc[idx, 'losses_contr'] / full_players['losses_contr'][0:11].sum()) * (final_losses * .99))
            else:
                wins_contr_list.append((full_players.loc[idx, 'wins_contr'] / full_players['wins_contr'][11:].sum()) * (final_wins * .01))
                losses_contr_list.append((full_players.loc[idx, 'losses_contr'] / full_players['losses_contr'][11:].sum()) * (final_losses * .01)) 

        full_players['wins_contr'] = wins_contr_list
        full_players['losses_contr'] = losses_contr_list
        full_players['val_contr'] = full_players['wins_contr'] + full_players['losses_contr']
        full_players['difference'] = full_players['wins_contr'] - full_players['losses_contr']
        # print(full_players)
        # final_player_predictions_df = final_player_predictions_df.merge(full_players, on='player_season_id', how='outer')
        final_full_player_predictions_df = final_full_player_predictions_df.append(full_players)
        # print(final_player_predictions_df)
        # sleep(1)


# full_wins_sum = full_players['wins_contr'].sum()
# print(full_wins_sum)
# full_losses_sum = full_players['losses_contr'].sum()
# full_wc_list = []
# full_lc_list = []
# id_list = []
# name_list = []

# full_df = pd.DataFrame()
# for idx, player in full_players['player_season_id'].iteritems():
#     name_list.append(full_players.loc[idx, 'player_name'])
#     id_list.append(player)
#     full_wc_list.append(full_players.loc[idx, 'wins_contr'] * injured_pct)
#     full_lc_list.append(full_players.loc[idx, 'losses_contr'] *injured_pct)

# full_df['player_name'] = name_list
# full_df['player_season_id'] = id_list
# full_df['wc'] = full_wc_list
# full_df['lc'] = full_wc_list

# injured_players = player_predictions_injured[player_predictions_injured['team_season_id'] == '1610612754_2020'].groupby(['player_season_id', 'player_name']).mean().reset_index().drop(columns='Unnamed: 0')
# injured_wins_sum = injured_players['wins_contr'].sum()
# print(injured_wins_sum)
# injured_losses_sum = injured_players['losses_contr'].sum()
# print(injured_players)
# injured_wc_list = []
# injured_lc_list = []
# id_list =[]
# name_list = []

# injured_df = pd.DataFrame()
# for idx, player in injured_players['player_season_id'].iteritems():
#     name_list.append(injured_players.loc[idx, 'player_name'])
#     id_list.append(player)
#     injured_wc_list.append(injured_players.loc[idx, 'wins_contr'] * injured_pct)
#     injured_lc_list.append(injured_players.loc[idx, 'losses_contr'] * injured_pct)

# injured_df['player_name'] = name_list
# injured_df['player_season_id'] = id_list
# injured_df['wc'] = injured_wc_list
# injured_df['lc'] = injured_wc_list

# final_df = full_df.merge(injured_df, on=['player_season_id', 'player_name'], how='outer')
# final_df['team_season_id'] = '1610612754_2020'
# final_df = final_df.fillna(0)
# print(final_df)
# final_df['wc'] = final_df['wc_x'] + final_df['wc_y']
# final_df['lc'] = final_df['lc_x'] + final_df['lc_y']
# final_df['wc_pct'] = final_df['wc'] / final_df['wc'].sum()
# final_df['lc_pct'] = final_df['lc'] / final_df['lc'].sum()
# final_df['wins_contr'] = final_df['wc_pct'] * final_wins
# final_df['losses_contr'] = final_df['lc_pct'] * final_losses
# final_df['val_contr'] = final_df['wins_contr'] + final_df['losses_contr']
# final_df['difference'] = final_df['wins_contr'] - final_df['losses_contr']

# final_df = final_df.drop(columns=['wc_x', 'wc_y', 'lc_x', 'lc_y', 'wct_pct', 'lc_pct', 'wc', 'wc'])


# print(final_injured_player_predictions_df.sort_values('wins_contr', ascending=False))
print(final_full_player_predictions_df.sort_values('wins_contr', ascending=False).reset_index(drop=True)[0:50])


conn = pg2.connect(dbname = 'postgres', host = "localhost")
conn.autocommit = True
engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/personal_website')
final_full_player_predictions_df.to_sql('player_predictions', con = engine, if_exists= "append", index=False)
final_team_predictions_df.to_sql('team_predictions', con = engine, if_exists= "append", index=False)
conn.close()

for team in final_full_player_predictions_df['team_season_id'].unique():
    print(final_full_player_predictions_df[final_full_player_predictions_df['team_season_id'] == team].sort_values('wins_contr', ascending=False).reset_index(drop=True))