import pandas as pd
from time import sleep
import csv

similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_5.csv')
print(similarity_df)
print(similarity_df[['id','player_name','season_end','2544_2019']].sort_values('2544_2019', ascending=False)[0:50])
print(similarity_df[similarity_df['player_name'] == 'Mitchell Robinson'])

def compare_players(df, player_id1, player_name2):
    print(df[df['player_name'] == player_name2][['id','player_name','season_end',player_id1]].sort_values(player_id1, ascending=False)[0:50])

# compare_players(similarity_df, '201142_2019', 'Devin Booker')

def group_players(similarity_df, threshold, classifier_column, start_column):
    group_dict = {}
    # print(similarity_df.columns)
    current_group_num = 0
    counter = 1
    for column in similarity_df.columns[start_column:]:
        print(str(counter) + ' / ' + str(len(similarity_df.columns[start_column:])))
        current_player_similar = similarity_df[similarity_df[column] >= threshold]
        id_list = current_player_similar[classifier_column].tolist()
        already_grouped = 0
        for key in group_dict:
            for player in id_list:
                if player in group_dict[key]:
                    current_group = list(group_dict[key])
                    current_group.extend(id_list)
                    group_dict[key] = set(current_group)
                    already_grouped = 1
                else:
                    pass
        if already_grouped == 0:
            group_dict[current_group_num] = id_list
            current_group_num += 1
            # group_dict[current_group_num]
        else:
            pass
        counter += 1
    
    return group_dict
    # with open('player_group.csv', 'w') as f:
    #     for key in group_dict.keys():
    #         f.write("%s,%s\n"%(key,group_dict[key]))


# player_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_5.csv')
# team_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_aligned.csv')

# grouped_teams = group_players(team_similarity_df, .55, 'team_season_id', 2)
# print(team_similarity_df)
# print(len(grouped_teams))
# print(player_similarity_df)
# grouped_players = group_players(player_similarity_df, .6, 'id', 4)
# print(len(grouped_players))






        
    
