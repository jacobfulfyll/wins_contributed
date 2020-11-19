import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
import psycopg2 as pg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from time import sleep
from clustering_functions import pca_transform_array, kmeans_silhouette, graph_elbow_gap, graph_hierarchical_dendorgram, graph_optics_neighborhoods, add_kmeans, add_agglomerative_hierarchical
#from rhetoric.rhetoric_dataset import sql_upload



conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()


all_stats_query = """SELECT team_id, player_id, season_end,
       player_name, COUNT(game_id) games_played, 
       AVG(two_pt_score_uast) two_pt_score_uast, AVG(two_pt_score_ast) two_pt_score_ast, AVG(two_pt_score_uast_oreb) two_pt_score_uast_oreb, AVG(two_pt_score_ast_oreb) two_pt_score_ast_oreb, AVG(missed_two_pt_fg) missed_two_pt_fg, AVG(positive_ft) positive_ft, AVG(three_pt_score_uast) three_pt_score_uast, AVG(three_pt_score_ast) three_pt_score_ast, AVG(three_pt_score_uast_oreb) three_pt_score_uast_oreb, AVG(three_pt_score_ast_oreb) three_pt_score_ast_oreb, AVG(missed_three_pt_fg) missed_three_pt_fg, AVG(negative_ft) negative_ft,
       AVG(ast_2pt) ast_2pt, AVG(ast_3pt) ast_3pt, AVG(ast_two_pt_oreb) ast_two_pt_oreb, AVG(ast_three_pt_oreb) ast_three_pt_oreb, AVG(to_score) to_score, AVG(sast_score) sast_score, AVG(ft_ast_score) ft_ast_score, 
       AVG(oreb_two_pt_uast) oreb_two_pt_uast, AVG(oreb_two_pt_ast) oreb_two_pt_ast, AVG(oreb_three_pt_uast) oreb_three_pt_uast, AVG(oreb_three_pt_ast) oreb_three_pt_ast, AVG(oreb_ft) oreb_ft, AVG(dreb_blk) dreb_blk, AVG(dreb_no_blk) dreb_no_blk, 
       AVG(stls_score) stls_score, AVG(blks_score) blks_score, AVG(dfg_score) dfg_score, AVG(positive_def_fouls) positive_def_fouls, AVG(negative_def_fouls) negative_def_fouls,
       AVG(value_contributed) value_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end, team_id;"""

val_contr_query = """SELECT losses.player_id, losses.player_name, losses.season_end, sum_wins_contributed, avg_wins_contributed, sum_losses_contributed, avg_losses_contributed, wins_avg_rank, losses_avg_rank
                    FROM (SELECT vc.player_id, vc.player_name, vc.season_end, SUM(vc.value_contributed) as sum_losses_contributed, AVG(vc.value_contributed) as avg_losses_contributed, AVG(dd.depth_chart_rank) as losses_avg_rank
                            FROM all_seasons_value_contributed as vc
                            INNER JOIN all_seasons_discrepancy_depth as dd
                            ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
                            WHERE vc.win_loss = 0
                            AND vc.season_type = 'Regular Season'
                            GROUP BY vc.player_id, vc.player_name, vc.season_end) as losses
                        LEFT OUTER JOIN (
                            SELECT vc.player_id, vc.player_name, vc.season_end, SUM(vc.value_contributed) as sum_wins_contributed, AVG(vc.value_contributed) as avg_wins_contributed, SUM(dd.discrepancy_total) as wins_discrepancy, AVG(dd.depth_chart_rank) as wins_avg_rank
                            FROM all_seasons_value_contributed as vc
                            INNER JOIN all_seasons_discrepancy_depth as dd
                            ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
                            WHERE vc.win_loss = 1
                            AND vc.season_type = 'Regular Season'
                            GROUP BY vc.player_id, vc.player_name, vc.season_end) as wins
                        ON (losses.player_id = wins.player_id AND losses.player_name = wins.player_name AND losses.season_end = wins.season_end)
                    ;"""


all_stats_df = pd.read_sql(all_stats_query, con=conn)
val_contr_df = pd.read_sql(val_contr_query, con=conn)
val_contr_df = val_contr_df.fillna(0)


conn.close()

# all_stats_df['abs_total_value'] = all_stats_df.iloc[:, 4:].sum(axis=1)
all_stats_df['id'] = [str(all_stats_df.loc[x, 'player_id']) + '_' + str(all_stats_df.loc[x, 'season_end']) for x in range(len(all_stats_df))]
all_stats_df = all_stats_df.sort_values('games_played', ascending=False).drop_duplicates(subset='id')
all_stats_df['total_value'] = all_stats_df.iloc[:, 5:36].sum(axis=1)

val_contr_df['id'] = [str(val_contr_df.loc[x, 'player_id']) + '_' + str(val_contr_df.loc[x, 'season_end']) for x in range(len(val_contr_df))]
val_contr_df = val_contr_df[['id', 'sum_wins_contributed', 'avg_wins_contributed', 'sum_losses_contributed', 'avg_losses_contributed', 'wins_avg_rank', 'losses_avg_rank']]

all_stats_df = all_stats_df.merge(val_contr_df, on='id', how='outer')
all_stats_df = all_stats_df.fillna(0)

X_scoring = all_stats_df.iloc[:,5:17].to_numpy()
X_passing = all_stats_df.iloc[:,17:24].to_numpy()
X_rebounds = all_stats_df.iloc[:,24:31].to_numpy()
X_defense = all_stats_df.iloc[:,31:36].to_numpy()
X_value = all_stats_df.iloc[:, 39:].to_numpy()


results_df = all_stats_df[['id', 'player_name', 'season_end', 'games_played']]

transform_list = [X_scoring]#, X_passing, X_rebounds, X_defense]#, X_value]
X_stats_list = []
for idx, stat_array in enumerate(transform_list):
    max_features = 5 
    min_var_explained = .95
    # PCA Transformation
    X_stats_list.append(pca_transform_array(stat_array, max_features, min_var_explained, scaler='normalize'))


# print(X_stats_list)

stat_titles = ['Scoring', 'Passing', 'Rebounds', 'Defense']#, 'Value']
# kmeans_cluster_lists = [[6,10,12,17], [6,8,11,16], [6,8,12,16], [6,9,13,17]]#, [5,7,11,15]]
# hierarchical_cluster_lists = [[6,10,12,17], [6,8,11,16], [6,8,12,16], [6,9,13,17]]#, [5,7,11,15]]
# kmeans_cluster_lists = [[6,10,12,17,19,24,26,33,36,41,49,54,61,68], [6,8,11,16,18,21,32,38,41,44,48,55,58,66], [6,8,12,16,20,28,31,36,40,46,48,57,61,67], [6,9,13,17,19,22,25,30,36,40,44,47,60,66], [5,7,11,15,18,22,28,32,39,42,45,49,60,63]]
# hierarchical_cluster_lists = [[6,10,12,17,19,24,26,33,36,41,49,54,61,68], [6,8,11,16,18,21,32,38,41,44,48,55,58,66], [6,8,12,16,20,28,31,36,40,46,48,57,61,67], [6,9,13,17,19,22,25,30,36,40,44,47,60,66], [5,7,11,15,18,22,28,32,39,42,45,49,60,63]]

# for idx, stat_df in enumerate(X_stats_list):
#     results_df = add_kmeans(kmeans_cluster_lists[idx], stat_titles[idx], stat_df, results_df)
#     results_df = add_agglomerative_hierarchical(hierarchical_cluster_lists[idx], stat_titles[idx], stat_df, results_df)

def df_row_comparison(df, column_id, start_column, total_columns, importance_factor=0):
    compared_df = pd.DataFrame({'id':df['id'], 'player_name':df['player_name'], 'season_end':df['season_end']})
    df = df.reset_index(drop=True)
    for current_row in range(len(df)):
        print('Current Row: ' + str(current_row) + ' / ' + str(len(df)))
        counter = 0
        column_list = []
        while counter < len(df):
            # print('Compare Row: ' + str(counter) + ' / ' + str(len(df)))
            same_columns = 0
            for column_num in range(total_columns):
                # print('Current Column: ' + str(column_num) + ' / ' + str(total_columns))
                if df.iloc[current_row, column_num + start_column] == df.iloc[counter, column_num + start_column]:
                    same_columns += 1
                else:
                    pass
            counter += 1
            column_list.append((same_columns / total_columns))
        compared_df[df.iloc[current_row, column_id]] = column_list

    return compared_df

# similar_seasons_df = df_row_comparison(results_df, 0, 2, 32)

# export_csv = similar_seasons_df.to_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_5.csv') 



for idx, stat_df in enumerate(X_stats_list):
    graph_elbow_gap(stat_df, KMeans(), stat_titles[idx], k_max=20)

for idx, stat_df in enumerate(X_stats_list):
    kmeans_silhouette(stat_df, range(3,20), stat_titles[idx])

for idx, stat_df in enumerate(X_stats_list):
    graph_hierarchical_dendorgram(stat_df, stat_titles[idx], color_split=.35)

# for idx, stat_df in enumerate(X_stats_list):
#     graph_optics_neighborhoods(stat_df)


# print(results_df)

def create_player_value_distribution_table(detail_df, stats_df_list):
    column_names = ['Scoring_1', 'Scoring_2', 'Scoring_3', 'Scoring_4', 'Scoring_5', 'Handling_1', 'Handling_2', 'Handling_3', 'Handling_4', 'Handling_5', 'Rebounding_1', 'Rebounding_2', 'Rebounding_3', 'Rebounding_4', 'Rebounding_5', 'Defense_1', 'Defense_2', 'Defense_3']
    counter = 0
    pca_df = pd.DataFrame()
    for stat_df in stats_df_list:
        for column in range(stat_df.shape[1]):
            append_df = detail_df
            append_df['player_id'] = [x.split('_')[0] for idx, x in append_df['id'].iteritems()]
            append_df['season_end'] = [x.split('_')[1] for idx, x in append_df['id'].iteritems()]
            append_df['stat_type'] = column_names[counter]
            append_df['pca_score'] = stat_df[:, column]
            counter += 1
            pca_df = pca_df.append(append_df)
    

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    pca_df.to_sql('pca_similarity_components', con = engine, if_exists= "append", index=False)
    conn.close()

    print(pca_df)

# create_player_value_distribution_table(results_df, X_stats_list)
        
        

'''
clusters = 40
player_km_transform, player_km_labels = kmeans(clusters, X_transformed, 'Player Clusters')
# print(y_km)
player_clusters_df = pd.DataFrame({'id':all_stats_df['id'], 'team_id':all_stats_df['team_id'], 'player_id':all_stats_df['player_id'], 'player_name':all_stats_df['player_name'], 'season_end':all_stats_df['season_end'], 'cluster':player_km_labels})
print(player_clusters_df)
# player_clusters_df['cluster'] = y_km
#two_pt_field_goals_df['score'] = y_km.score(X_scaled)
for idx in range(clusters):
    player_clusters_df[str(idx)] = player_km_transform[:, idx]

for idx in range(clusters):
    print(player_clusters_df[player_clusters_df['cluster'] == idx].sort_values(str(idx)))

print(player_clusters_df)

team_clusters = []
team_ids = []
team_seasons = []
for team in player_clusters_df['team_id'].unique():
    for season_end in player_clusters_df['season_end'].unique():
        team_season_df = player_clusters_df[(player_clusters_df['team_id'] == team) & (player_clusters_df['season_end'] == season_end)]
        print(team_season_df)
        team_season_df = team_season_df.merge(val_contr_df, on='id')
        print(team_season_df)
        team_season_df_val = team_season_df.sort_values('val_contr', ascending=False)
        print(team_season_df_val)
        current_team = team_season_df_val['cluster'][0:8].tolist()
        # print(wins_query.info())
        # print(type(team))
        # print(type(season_end))
        # print(wins_df[(wins_df['team_id'] == team) & (wins_df['season_end'] == season_end)].loc[0, 'wins'])
        # print(type(wins_df[(wins_df['team_id'] == team) & (wins_df['season_end'] == season_end)].loc[0, 'wins']))
        current_team.append(wins_df[(wins_df['team_id'] == team) & (wins_df['season_end'] == season_end)].reset_index(drop=True).loc[0, 'wins'])
        current_team.append(losses_df[(losses_df['team_id'] == team) & (losses_df['season_end'] == season_end)].reset_index(drop=True).loc[0, 'losses'])
        team_clusters.append(current_team)

        team_ids.append(team_season_df_val['team_id'].tolist())
        team_seasons.append(team_season_df_val['season_end'].tolist())

team_clusters_array = np.array(team_clusters)
print(team_clusters_array.shape)


min_max_scaler = preprocessing.MinMaxScaler()
X_scaled = min_max_scaler.fit_transform(team_clusters_array)

# km_clusters = 18
# team_km_transform, team_km_labels= kmeans(km_clusters, X_scaled, 'Team Clusters')
# team_km_df = pd.DataFrame({'team_id':wins_df['team_id'], 'season_end':wins_df['season_end'], 'cluster':team_km_labels})

# for idx in range(km_clusters):
#     team_km_df[str(idx)] = team_km_transform[:, idx]

# for idx in range(km_clusters):
#     print(team_km_df[team_km_df['cluster'] == idx].sort_values(str(idx)))


ah_clusters = 10
team_ah_labels = agglomerative_hierarchical(ah_clusters, team_clusters_array, 'Team Clusters')
team_ah_df = pd.DataFrame({'team_id':wins_df['team_id'], 'season_end':wins_df['season_end'], 'cluster':team_ah_labels})

print(team_ah_labels.shape)

# for idx in range(ah_clusters):
#     team_ah_df[str(idx)] = team_ah_predicted[:, idx]

for idx in range(ah_clusters):
    print(team_ah_df[team_ah_df['cluster'] == idx])
'''