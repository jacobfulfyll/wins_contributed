import csv
import pandas as pd
import numpy as np
from player_groups import group_players
import psycopg2 as pg2
from time import sleep
from clustering_functions import normalize

player_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_5.csv')


# grouped_players = group_players(similarity_df, .8)

# print(len(grouped_players))

# plasyer_group_dict = {}

# new_dict = dict([(value, key) for key, value in grouped_players.items()])

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

wins_contr_query = """SELECT team_id, player_id, season_end, SUM(value_contributed) wins_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        AND win_loss = 1
                        GROUP BY player_id, player_name, season_end, team_id;"""

losses_contr_query = """SELECT team_id, player_id, season_end, player_name, SUM(value_contributed) wins_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        AND win_loss = 0
                        GROUP BY player_id, player_name, season_end, team_id;"""

wins_query = """SELECT team_id, player_id, season_end, player_name, SUM(value_contributed) wins_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        AND win_loss = 1
                        GROUP BY player_id, player_name, season_end, team_id;"""

losses_query = """SELECT team_id, player_id, season_end, player_name, SUM(value_contributed) wins_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        AND win_loss = 0
                        GROUP BY player_id, player_name, season_end, team_id;"""

all_stats_query = """SELECT team_id, player_id, season_end, player_name, SUM(value_contributed) as val_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end, team_id;"""

roster_query = """SELECT *
                        FROM league_rosters
                        WHERE season_end = '2019';"""



wins_df = pd.read_sql(wins_query, con=conn)
losses_df = pd.read_sql(losses_query, con=conn)
wins_contr_df = pd.read_sql(wins_contr_query, con=conn)
losses_contr_df = pd.read_sql(losses_contr_query, con=conn)

all_stats_df = pd.read_sql(all_stats_query, con=conn)
roster_df = pd.read_sql(roster_query, con=conn)
injured_players = ['Kevin Durant', 'DeMarcus Cousins', 'John Wall', 'Andre Iguodala', 'Darius Miller']
print(len(roster_df))
for player in injured_players:
    roster_df = roster_df[roster_df['player_name'] != player]

roster_df = roster_df.reset_index(drop=True)
print(len(roster_df))
all_stats_df['team_season_id'] = [str(all_stats_df.loc[x, 'team_id']) + '_' + str(all_stats_df.loc[x, 'season_end']) for x in range(len(all_stats_df))]
all_stats_df['player_season_id'] = [str(all_stats_df.loc[x, 'player_id']) + '_' + str(all_stats_df.loc[x, 'season_end']) for x in range(len(all_stats_df))]
wins_contr_df['team_season_id'] = [str(wins_contr_df.loc[x, 'team_id']) + '_' + str(wins_contr_df.loc[x, 'season_end']) for x in range(len(wins_contr_df))]
wins_contr_df['player_season_id'] = [str(wins_contr_df.loc[x, 'player_id']) + '_' + str(wins_contr_df.loc[x, 'season_end']) for x in range(len(wins_contr_df))]
roster_df['team_season_id'] = [str(roster_df.loc[x, 'team_id']) + '_' + str(int(roster_df.loc[x, 'season_end']) + 1) for x in range(len(roster_df))]
roster_df['player_season_id'] = [str(roster_df.loc[x, 'player_id']) + '_' + str(roster_df.loc[x, 'season_end']) for x in range(len(roster_df))]

wins_contr_df = wins_contr_df[['team_season_id', 'player_season_id', 'wins_contr']]
all_stats_df = all_stats_df[['team_season_id', 'player_season_id', 'val_contr']]
all_stats_df = all_stats_df.merge(wins_contr_df, on=['team_season_id', 'player_season_id'])
roster_df = roster_df[['team_season_id', 'player_season_id']]

val_contr_list = []
wins_contr_list = []
for idx, player in roster_df['player_season_id'].iteritems():
    try:
        val_contr_list.append(all_stats_df[all_stats_df['player_season_id'] == player].reset_index(drop=True).loc[0, 'val_contr'])
        wins_contr_list.append(all_stats_df[all_stats_df['player_season_id'] == player].reset_index(drop=True).loc[0, 'wins_contr'])
    except:
        val_contr_list.append(0)
        wins_contr_list.append(0)

roster_df['val_contr'] = val_contr_list
roster_df['wins_contr'] = wins_contr_list

all_stats_df = all_stats_df.append(roster_df)

team_makeup_df = pd.DataFrame(columns=['team_season_id', '1','2','3','4','5','6','7','8','9', '10'])


for team in all_stats_df['team_season_id'].unique():
    team_df = all_stats_df[all_stats_df['team_season_id'] == team].sort_values('val_contr', ascending=False).reset_index(drop=True)
    row_list = [team]
    for idx in range(10):
        row_list.append(team_df.loc[idx, 'player_season_id'])
    team_makeup_df.loc[len(team_makeup_df)] = row_list

print(team_makeup_df[team_makeup_df['team_season_id'] == '1610612744_2018'])
print(team_makeup_df[team_makeup_df['team_season_id'] == '1610612764_2019'])


def team_comparison(teams_df, players_df, contr_df):
    compared_df = pd.DataFrame({'team_season_id':teams_df['team_season_id']})

    for current_row in range(len(teams_df)):
        print('Current Row: ' + str(current_row) + ' / ' + str(len(teams_df)))
        counter = 0
        column_list = []
        while counter < len(teams_df):
            # print('Compare Row: ' + str(counter) + ' / ' + str(len(df)))
            similarity_score = 0
            similarity_total = 1000
            value_list = [235, 160, 134, 116, 101, 81, 74, 63, 36]
            for column_num in range(10):
                # print('Current Column: ' + str(column_num) + ' / ' + str(total_columns))
                primary_score = 0
                secondary_score = 0
                usage_difference = abs((contr_df[(contr_df['player_season_id'] == teams_df.iloc[counter, column_num + 1]) & (contr_df['team_season_id'] == teams_df.iloc[counter, 0])].reset_index(drop=True).loc[0, 'wins_contr'] / 82) - (contr_df[(contr_df['player_season_id'] == teams_df.iloc[current_row, column_num + 1]) & (contr_df['team_season_id'] == teams_df.iloc[current_row, 0])].reset_index(drop=True).loc[0, 'wins_contr'] / 82)) 
                try:
                    primary_score = (players_df[players_df['id'] == teams_df.iloc[counter, column_num + 1]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num + 1]] * value_list[column_num])
                    remaining_score = value_list[column_num] - primary_score
                    if column_num == 0:
                        secondary_score = (players_df[players_df['id'] == teams_df.iloc[counter, column_num + 2]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]] * remaining_score)
                    elif column_num == 9:
                        secondary_score = (players_df[players_df['id'] == teams_df.iloc[counter, column_num]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]] * remaining_score)
                    else:
                        if players_df[players_df['id'] == teams_df.iloc[counter, column_num]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]] > players_df[players_df['id'] == teams_df.iloc[counter, column_num + 2]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]]:
                            secondary_score = (players_df[players_df['id'] == teams_df.iloc[counter, column_num]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]] * remaining_score)
                        else:
                            secondary_score = (players_df[players_df['id'] == teams_df.iloc[counter, column_num + 2]].reset_index(drop=True).loc[0, teams_df.iloc[current_row, column_num]] * remaining_score)
                            
                except:
                    similarity_score += 0

                similarity_score += (primary_score + secondary_score) * (1 - usage_difference)

            counter += 1
            column_list.append((similarity_score / similarity_total))
        compared_df[teams_df.iloc[current_row, 0]] = column_list
        print(compared_df)
    return compared_df

similar_teams_df = team_comparison(team_makeup_df, player_similarity_df, all_stats_df)

export_csv = similar_teams_df.to_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020.csv') 

def align_team_similarity(team_similarity_df):
    aligned_team_similarity = pd.DataFrame({'team_season_id':team_similarity_df['team_season_id']})
    print(team_similarity_df)
    counter = 1
    for column in team_similarity_df.columns[2:]:
        print(str(counter) + ' / ' + str(len(team_similarity_df.columns[2:])))
        avg_list = []
        for idx in range(len(team_similarity_df)):
            current_team_sim = team_similarity_df.loc[idx, column]
            compare_team_sim = team_similarity_df[team_similarity_df['team_season_id'] == column].reset_index(drop=True).loc[0, team_similarity_df.loc[idx, 'team_season_id']]
            avg_list.append((current_team_sim + compare_team_sim) / 2)
        
        counter += 1
        aligned_team_similarity[column] = avg_list
    
    export_csv = aligned_team_similarity.to_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_aligned.csv')
    print(aligned_team_similarity)

similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_injured_excluded.csv')

align_team_similarity(similarity_df)



def normalize_team_similarity(df):
    normalizing_list = []
    normalized_df = pd.DataFrame({'team_season_id':df['team_season_id']})
    for column in df.columns[2:]:
        normalizing_list.append(df[column].to_list())
    
    normalizing_list = [x for x in normalizing_list if x != 1]
    normalizing_array = np.array(normalizing_list).reshape(-1,1)
    normalized = normalize(normalizing_array)

    counter = 0
    for column in df.columns[2:]:
        normalized_list = []
        for idx in range(len(df)): 
            normalized_list.append(normalized[counter])
            counter += 1
        normalized_df[column] = normalized_list
    
    print(df)
    export_csv = df.to_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_normalized.csv')


def find_similar_teams(team1):
    similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix.csv')
    print(similarity_df)
    print(similarity_df[['team_season_id',team1]].sort_values(team1, ascending=False)[0:50])

# find_similar_teams('1610612764_2018')







