import pandas as pd
import numpy as np
from sklearn import preprocessing
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering, KMeans, SpectralClustering
import psycopg2 as pg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import hdbscan
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
#from rhetoric.rhetoric_dataset import sql_upload



conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

all_stats_query = """SELECT COUNT(game_id) games_played, player_id, season_end,
       player_name, SUM(two_pt_score_uast) two_pt_score_uast, SUM(three_pt_score_uast) three_pt_score_uast,
       SUM(two_pt_score_ast) two_pt_score_ast, SUM(three_pt_score_ast) three_pt_score_ast, SUM(two_pt_score_uast_oreb) two_pt_score_uast_oreb,
       SUM(three_pt_score_uast_oreb) three_pt_score_uast_oreb, SUM(two_pt_score_ast_oreb) two_pt_score_ast_oreb,
       SUM(three_pt_score_ast_oreb) three_pt_score_ast_oreb, SUM(ast_2pt) ast_2pt, SUM(ast_3pt) ast_3pt, SUM(ast_two_pt_oreb) ast_two_pt_oreb,
       SUM(ast_three_pt_oreb) ast_three_pt_oreb, SUM(oreb_two_pt_uast) oreb_two_pt_uast, SUM(oreb_two_pt_ast) oreb_two_pt_ast,
       SUM(oreb_three_pt_uast) oreb_three_pt_uast, SUM(oreb_three_pt_ast) oreb_three_pt_ast, SUM(oreb_ft) oreb_ft, 
       SUM(dreb_blk) dreb_blk, SUM(dreb_no_blk) dreb_no_blk, ABS(SUM(to_score)) to_score, SUM(stls_score) stls_score, 
       SUM(blks_score) blks_score, SUM(positive_ft) positive_ft, ABS(SUM(negative_ft)) negative_ft, SUM(dfg_score) dfg_score,
       SUM(sast_score) sast_score, SUM(ft_ast_score) ft_ast_score, ABS(SUM(missed_two_pt_fg)) missed_two_pt_fg,
       ABS(SUM(missed_three_pt_fg)) missed_three_pt_fg, SUM(positive_def_fouls) positive_def_fouls,
       ABS(SUM(negative_def_fouls)) negative_def_fouls
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end;"""

all_stats_df = pd.read_sql(all_stats_query, con=conn)
conn.close()

all_stats_df['abs_total_value'] = all_stats_df.iloc[:, 4:].sum(axis=1)
all_stats_df['id'] = [str(all_stats_df.loc[x, 'player_id']) + '_' + str(all_stats_df.loc[x, 'season_end']) for x in range(len(all_stats_df))]

print(all_stats_df)

min_max_scaler = preprocessing.MinMaxScaler()

for column in all_stats_df.columns[4:-2]:
    all_stats_df[column] = all_stats_df[column] / all_stats_df['abs_total_value']
    all_stats_df[column] = min_max_scaler.fit_transform(all_stats_df[column].to_numpy().reshape(-1, 1))

# print(all_stats_df.iloc[:, [4,6,8,10,31]])

all_stats_df = all_stats_df.fillna(0)


X = all_stats_df.iloc[:, 4:-2].to_numpy()
#print(X)

pca_model = PCA(n_components=10)
X_fit = pca_model.fit(X)
print(X_fit.explained_variance_ratio_)
print(X_fit.explained_variance_ratio_[0:10].sum())
X_transformed = X_fit.transform(X)
print(X_transformed)
print(X_transformed.shape)

clusters= 12

km = KMeans(n_clusters=clusters, random_state=0, n_init=10, algorithm='full', n_jobs=-1)
y_km_transform = km.fit_transform(X_transformed)
y_km_labels = km.labels_

kmeans_df = pd.DataFrame({'id':all_stats_df['id'], 'player_name':all_stats_df['player_name'], 'cluster':y_km_labels})

for i in range(clusters):
    kmeans_df[i] = y_km_transform[:, i]

for idx in range(clusters):
    print(kmeans_df[kmeans_df['cluster'] == idx].iloc[:, :50].sort_values(idx))


# distortions = []
# for i in range(1, 24):
#     km = KMeans(
#         n_clusters=i, init='random',
#         n_init=10, max_iter=300,
#         tol=1e-04, random_state=0
#     )
#     km.fit(X_transformed)
#     distortions.append(km.inertia_)

# # plot
# plt.plot(range(1, 24), distortions, marker='o')
# plt.xlabel('Number of clusters')
# plt.ylabel('Distortion')
# plt.show()


# data = all_stats_df.iloc[:, 4:-2].to_numpy()

# data, _ = make_blobs(3034)

# clusterer = hdbscan.HDBSCAN(min_cluster_size=10)
# cluster_labels = clusterer.fit_predict(data)
# print(cluster_labels.shape)
# all_stats_df['cluster'] = cluster_labels

# print(all_stats_df)