import pandas as pd
from Stat_Calculations.yearly_stats import compile_team_yearly_stats, compile_yearly_stats, season_rankings_by_game
from Stat_Calculations.compile_data import create_stats_df
import numpy as np
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from sklearn import preprocessing
import psycopg2 as pg2
from sqlalchemy import create_engine

def base_stats_df():
    print('#1')
    base_stats_df = create_stats_df()
    base_stats_df = base_stats_df[base_stats_df['season_type'] == 'Regular Season']

    base_stats_df['jacob_absolute_value'] = base_stats_df['points_score'].abs() + base_stats_df['assists_score'].abs() + base_stats_df['orebs_score'].abs() + base_stats_df['drebs_score'].abs() + base_stats_df['to_score'].abs() + base_stats_df['stls_score'].abs() + base_stats_df['blocks_score'].abs() + base_stats_df['ft_score'].abs() + base_stats_df['dfg_score'].abs() + base_stats_df['sast_score'].abs() + base_stats_df['ft_ast_score'].abs() + base_stats_df['missed_fg_score'].abs() + base_stats_df['def_fouls_score'].abs()
    base_stats_df['pts_contr'] = (base_stats_df['points_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['ast_contr'] = (base_stats_df['assists_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['orebs_contr'] = (base_stats_df['orebs_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['drebs_contr'] = (base_stats_df['drebs_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['to_contr'] = (base_stats_df['to_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['stls_contr'] = (base_stats_df['stls_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['blocks_contr'] = (base_stats_df['blocks_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['ft_contr'] = (base_stats_df['ft_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['dfg_contr'] = (base_stats_df['dfg_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['sast_contr'] = (base_stats_df['sast_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['ft_ast_contr'] = (base_stats_df['ft_ast_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['missed_fg_contr'] = (base_stats_df['missed_fg_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df['def_fouls_contr'] = (base_stats_df['def_fouls_score'] / base_stats_df['jacob_absolute_value']) * base_stats_df['wins_contr']
    base_stats_df = base_stats_df[['season_end', 'player_id', 'player_name', 'pts_contr', 'ast_contr', 'orebs_contr', 'drebs_contr', 'to_contr', 'stls_contr', 'blocks_contr', 'ft_contr', 'dfg_contr', 'sast_contr', 'ft_ast_contr', 'missed_fg_contr', 'def_fouls_contr']]


    sum_base_stats_df = base_stats_df.groupby(['player_id','season_end', 'player_name'], as_index=False)
    sum_base_stats_df = sum_base_stats_df.aggregate(np.sum)
    sum_base_stats_df = sum_base_stats_df.rename(columns={"pts_contr": "pts_contr_sum", "ast_contr": "ast_contr_sum", 
                                                    "orebs_contr": "orebs_contr_sum", "drebs_contr": "drebs_contr_sum",
                                                    "to_contr": "to_contr_sum", "stls_contr": "stls_contr_sum",
                                                    "blocks_contr": "blocks_contr_sum", "ft_contr": "ft_contr_sum",
                                                    "dfg_contr": "dfg_contr_sum", "sast_contr": "sast_contr_sum",
                                                    "ft_ast_contr": "ft_ast_contr_sum", "missed_fg_contr": "missed_fg_contr_sum",
                                                    "def_fouls_contr": "def_fouls_contr_sum"})

    mean_base_stats_df = base_stats_df.groupby(['player_id','season_end', 'player_name'], as_index=False)
    mean_base_stats_df = mean_base_stats_df.aggregate(np.mean)
    mean_base_stats_df = mean_base_stats_df.rename(columns={"pts_contr": "pts_contr_avg", "ast_contr": "ast_contr_avg", 
                                                    "orebs_contr": "orebs_contr_avg", "drebs_contr": "drebs_contr_avg",
                                                    "to_contr": "to_contr_avg", "stls_contr": "stls_contr_avg",
                                                    "blocks_contr": "blocks_contr_avg", "ft_contr": "ft_contr_avg",
                                                    "dfg_contr": "dfg_contr_avg", "sast_contr": "sast_contr_avg",
                                                    "ft_ast_contr": "ft_ast_contr_avg", "missed_fg_contr": "missed_fg_contr_avg",
                                                    "def_fouls_contr": "def_fouls_contr_avg"})

    
    base_stats_df = sum_base_stats_df.merge(mean_base_stats_df, on=['player_id','season_end', 'player_name'])

    return base_stats_df
# base_stats_df()

def yearly_stats_df():
    print('#2')
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    # SQL Pull
    team_yearly_stats = """SELECT *
                        FROM yearly_stats_by_team"""
    yearly_stats = """SELECT *
                        FROM yearly_stats_by_season"""

    team_yearly_stats = pd.read_sql(team_yearly_stats, con=conn)
    team_yearly_stats = team_yearly_stats[team_yearly_stats['season_type'] == 'Regular Season']
    team_yearly_stats = team_yearly_stats.drop(columns=['season_type', 'team_id', 'wins_contr', 'wins_contr_in_loss'])
    # print('team_yearly stats')
    # print(team_yearly_stats[team_yearly_stats['player_id'] == 202355])
    

    yearly_stats = pd.read_sql(yearly_stats, con=conn)
    yearly_stats = yearly_stats[yearly_stats['season_type'] == 'Regular Season']
    yearly_stats['pct_of_wins'] = yearly_stats['wins_contr'] / yearly_stats['wins']
    yearly_stats = yearly_stats.drop(columns=['wins', 'losses', 'games_played', 'season_type'])
    # print('yearly stats')
    # print(yearly_stats[yearly_stats['player_id'] == 202355])

    conn.close()

    return yearly_stats.merge(team_yearly_stats, on=['player_id','season_end', 'player_name'])

#yearly_stats_df()

def game_rank_df():
    print('#3')
    tc_rank_2014 = season_rankings_by_game(season_end=2014, win_loss='both', season_type='Regular Season')
    tc_rank_2014['season_end'] = 2014
    tc_rank_2015 = season_rankings_by_game(season_end=2015, win_loss='both', season_type='Regular Season')
    tc_rank_2015['season_end'] = 2015
    tc_rank_2016 = season_rankings_by_game(season_end=2016, win_loss='both', season_type='Regular Season')
    tc_rank_2016['season_end'] = 2016
    tc_rank_2017 = season_rankings_by_game(season_end=2017, win_loss='both', season_type='Regular Season')
    tc_rank_2017['season_end'] = 2017
    tc_rank_2018 = season_rankings_by_game(season_end=2018, win_loss='both', season_type='Regular Season')
    tc_rank_2018['season_end'] = 2018
    tc_rank_2019 = season_rankings_by_game(season_end=2019, win_loss='both', season_type='Regular Season')
    tc_rank_2019['season_end'] = 2019

    wc_rank_2014 = season_rankings_by_game(season_end=2014, win_loss=1, season_type='Regular Season')
    wc_rank_2014['season_end'] = 2014
    wc_rank_2015 = season_rankings_by_game(season_end=2015, win_loss=1, season_type='Regular Season')
    wc_rank_2015['season_end'] = 2015
    wc_rank_2016 = season_rankings_by_game(season_end=2016, win_loss=1, season_type='Regular Season')
    wc_rank_2016['season_end'] = 2016
    wc_rank_2017 = season_rankings_by_game(season_end=2017, win_loss=1, season_type='Regular Season')
    wc_rank_2017['season_end'] = 2017
    wc_rank_2018 = season_rankings_by_game(season_end=2018, win_loss=1, season_type='Regular Season')
    wc_rank_2018['season_end'] = 2018
    wc_rank_2019 = season_rankings_by_game(season_end=2019, win_loss=1, season_type='Regular Season')
    wc_rank_2019['season_end'] = 2019



    tc_games_rank = tc_rank_2014.append([tc_rank_2015, tc_rank_2016, tc_rank_2017, tc_rank_2018, tc_rank_2019])
    tc_games_rank = tc_games_rank.rename(columns={"win_rank": "total_rank_games"})
    wc_games_rank = wc_rank_2014.append([wc_rank_2015, wc_rank_2016, wc_rank_2017, wc_rank_2018, wc_rank_2019])
    wc_games_rank = wc_games_rank.rename(columns={"win_rank": "win_rank_games"})
    all_seasons_games_rank = tc_games_rank.merge(wc_games_rank, on=['player_id', 'player_name','season_end'])

    all_seasons_games_rank = all_seasons_games_rank.reset_index(drop=True)

    return all_seasons_games_rank

def clustering_df():
    
    clustering_df = base_stats_df().merge(yearly_stats_df(), on=['player_id', 'player_name','season_end'])
    clustering_df = clustering_df.merge(game_rank_df(), on=['player_id', 'player_name','season_end'])
    clustering_df = clustering_df.reset_index(drop=True)
    return clustering_df
# clustering_df()

def nearest_neighbors_df(df):
    X = pd.DataFrame()
    y = pd.DataFrame()
    clustering_df = df.replace([np.inf, -np.inf], np.nan)
    clustering_df = clustering_df.fillna(0)
    clustering_df = clustering_df.drop_duplicates()
    # print(clustering_df)
    # print(clustering_df.columns)
    print(clustering_df[clustering_df['player_id'] == 1629011])
    y['player_id'] = clustering_df['player_id']
    y['season_end'] = clustering_df['season_end']
    y['player_name'] = clustering_df['player_name']
    X['pos_offense'] = clustering_df['pts_contr_avg']  + clustering_df['ast_contr_avg'] + clustering_df['ft_ast_contr_avg'] + clustering_df['ft_contr_avg']
    X['neg_offense'] =  clustering_df['missed_fg_contr_avg'] + clustering_df['to_contr_avg']
    X['hustle'] = clustering_df['orebs_contr_avg'] + clustering_df['drebs_contr_avg'] + clustering_df['sast_contr_avg']
    X['defense'] = clustering_df['stls_contr_avg'] + clustering_df['blocks_contr_avg'] + clustering_df['dfg_contr_avg'] + clustering_df['def_fouls_contr_avg']
    X['rank'] = clustering_df['tc_rank_team'] / clustering_df['total_rank_games']
    X['wins'] = clustering_df['wc_lc_ratio'] * clustering_df['pct_of_wins']

    y = y.reset_index(drop=True)
    X = X.reset_index(drop=True)

    X = X.to_numpy()
    min_max_scaler = preprocessing.MinMaxScaler()
    X_scaled = min_max_scaler.fit_transform(X)
    
    print('the fit has begun')
    neigh = NearestNeighbors(n_neighbors=6, metric='cosine')
    neigh.fit(X_scaled)
    
    
    neighbors_df = pd.DataFrame()
    neighbors_df['similar_player_1_id'] = 0
    neighbors_df['similar_player_1_season_end'] = 0
    neighbors_df['similar_player_1_name'] = 0
    neighbors_df['similar_player_1_distance'] = 0
    neighbors_df['similar_player_2_id'] = 0
    neighbors_df['similar_player_2_season_end'] = 0
    neighbors_df['similar_player_2_name'] = 0
    neighbors_df['similar_player_2_distance'] = 0
    neighbors_df['similar_player_3_id'] = 0
    neighbors_df['similar_player_3_season_end'] = 0
    neighbors_df['similar_player_3_name'] = 0
    neighbors_df['similar_player_3_distance'] = 0
    neighbors_df['similar_player_4_id'] = 0
    neighbors_df['similar_player_4_season_end'] = 0
    neighbors_df['similar_player_4_name'] = 0
    neighbors_df['similar_player_4_distance'] = 0
    neighbors_df['similar_player_5_id'] = 0
    neighbors_df['similar_player_5_season_end'] = 0
    neighbors_df['similar_player_5_name'] = 0
    neighbors_df['similar_player_5_distance'] = 0
    similar_player_1_id_list = []
    similar_player_2_id_list = []
    similar_player_3_id_list = []
    similar_player_4_id_list = []
    similar_player_5_id_list = []
    similar_player_1_season_end_list = []
    similar_player_2_season_end_list = []
    similar_player_3_season_end_list = []
    similar_player_4_season_end_list = []
    similar_player_5_season_end_list = []
    similar_player_1_name_list = []
    similar_player_2_name_list = []
    similar_player_3_name_list = []
    similar_player_4_name_list = []
    similar_player_5_name_list = []
    similar_player_1_distance_list = []
    similar_player_2_distance_list = []
    similar_player_3_distance_list = []
    similar_player_4_distance_list = []
    similar_player_5_distance_list = []
    for idx in range(len(X)):
        #print('Neighbors Loop: ' + str(idx) + ' / ' + str(len(X)))
        neighbors = neigh.kneighbors(X_scaled[idx, :].reshape(1, -1))
        distance_list = neighbors[0].tolist()
        for idx, neighbors in enumerate(neighbors[1]):
            neighbors = neighbors[1:]

            for counter, player in enumerate(neighbors):
                if counter == 0:
                    similar_player_1_id_list.append(y.iloc[player, 0])
                    similar_player_1_season_end_list.append(y.iloc[player, 1])
                    similar_player_1_name_list.append(y.iloc[player, 2])
                    similar_player_1_distance_list.append(distance_list[idx][1])
                elif counter == 1:
                    similar_player_2_id_list.append(y.iloc[player, 0])
                    similar_player_2_season_end_list.append(y.iloc[player, 1])
                    similar_player_2_name_list.append(y.iloc[player, 2])
                    similar_player_2_distance_list.append(distance_list[idx][2])
                elif counter == 2:
                    similar_player_3_id_list.append(y.iloc[player, 0])
                    similar_player_3_season_end_list.append(y.iloc[player, 1])
                    similar_player_3_name_list.append(y.iloc[player, 2])
                    similar_player_3_distance_list.append(distance_list[idx][3])
                elif counter == 3:
                    similar_player_4_id_list.append(y.iloc[player, 0])
                    similar_player_4_season_end_list.append(y.iloc[player, 1])
                    similar_player_4_name_list.append(y.iloc[player, 2])
                    similar_player_4_distance_list.append(distance_list[idx][4])
                else:
                    similar_player_5_id_list.append(y.iloc[player, 0])
                    similar_player_5_season_end_list.append(y.iloc[player, 1])
                    similar_player_5_name_list.append(y.iloc[player, 2])
                    similar_player_5_distance_list.append(distance_list[idx][5])
    

    neighbors_df['positive_offense'] = X[:, 0]
    neighbors_df['negative_offense'] = X[:, 1]
    neighbors_df['hustle_stats'] = X[:, 2]
    neighbors_df['defense_stats'] = X[:, 3]
    neighbors_df['alpha_measure'] = X[:, 4]
    neighbors_df['winning_factor'] = X[:, 5]
    neighbors_df['similar_player_1_id'] = similar_player_1_id_list
    neighbors_df['similar_player_1_season_end'] = similar_player_1_season_end_list
    neighbors_df['similar_player_1_name'] = similar_player_1_name_list
    neighbors_df['similar_player_1_distance'] = similar_player_1_distance_list
    neighbors_df['similar_player_2_id'] = similar_player_2_id_list
    neighbors_df['similar_player_2_season_end'] = similar_player_2_season_end_list
    neighbors_df['similar_player_2_name'] = similar_player_2_name_list
    neighbors_df['similar_player_2_distance'] = similar_player_2_distance_list
    neighbors_df['similar_player_3_id'] = similar_player_3_id_list
    neighbors_df['similar_player_3_season_end'] = similar_player_3_season_end_list
    neighbors_df['similar_player_3_name'] = similar_player_3_name_list
    neighbors_df['similar_player_3_distance'] = similar_player_3_distance_list
    neighbors_df['similar_player_4_id'] = similar_player_4_id_list
    neighbors_df['similar_player_4_season_end'] = similar_player_4_season_end_list
    neighbors_df['similar_player_4_name'] = similar_player_4_name_list
    neighbors_df['similar_player_4_distance'] = similar_player_4_distance_list
    neighbors_df['similar_player_5_id'] = similar_player_5_id_list
    neighbors_df['similar_player_5_season_end'] = similar_player_5_season_end_list
    neighbors_df['similar_player_5_name'] = similar_player_5_name_list
    neighbors_df['similar_player_5_distance'] = similar_player_5_distance_list
    # print('neighbors')
    # print(neighbors_df)
    # print('player info')
    # print(y)
    # print(y[y['player_id']==1629011])
    # print(neighbors_df[neighbors_df['player_id']==1629011])
    neighbors_df = pd.merge(y, neighbors_df, left_index=True, right_index=True)
    # print(neighbors_df)
    # print(neighbors_df.sort_values('positive_offense', ascending= False))

    neighbors_df['positive_offense'] = neighbors_df['positive_offense'].values.astype(int)
    neighbors_df['negative_offense'] = neighbors_df['negative_offense'].values.astype(int)
    neighbors_df['hustle_stats'] = neighbors_df['hustle_stats'].values.astype(int)
    neighbors_df['defense_stats'] = neighbors_df['defense_stats'].values.astype(float) 
    neighbors_df['alpha_measure'] = neighbors_df['alpha_measure'].values.astype(float)
    neighbors_df['winning_factor'] = neighbors_df['winning_factor'].values.astype(float)

    similarity_rank_1_df = pd.DataFrame()
    similarity_rank_2_df = pd.DataFrame()
    similarity_rank_3_df = pd.DataFrame()
    similarity_rank_4_df = pd.DataFrame()
    similarity_rank_5_df = pd.DataFrame()

    similarity_rank_1_df['distance'] = neighbors_df['similar_player_1_distance']
    similarity_rank_2_df['distance'] = neighbors_df['similar_player_2_distance']
    similarity_rank_3_df['distance'] = neighbors_df['similar_player_3_distance']
    similarity_rank_4_df['distance'] = neighbors_df['similar_player_4_distance']
    similarity_rank_5_df['distance'] = neighbors_df['similar_player_5_distance']

    similarity_rank_1_df['rank'] = 1
    similarity_rank_2_df['rank'] = 2
    similarity_rank_3_df['rank'] = 3
    similarity_rank_4_df['rank'] = 4
    similarity_rank_5_df['rank'] = 5
    
    
    similarity_rank_df = similarity_rank_1_df.append([similarity_rank_2_df, similarity_rank_3_df, similarity_rank_4_df, similarity_rank_5_df]).reset_index()
    #print(similarity_rank_df)
    similarity_rank_df = similarity_rank_df.sort_values('distance')
    similarity_rank_df = similarity_rank_df.reset_index(drop=True).reset_index()
    #print(similarity_rank_df)
    similarity_rank_df = similarity_rank_df.rename(columns={"level_0":"similarity_rank"})
    similarity_rank_df = similarity_rank_df[['index', 'similarity_rank', 'rank']]
    
    similarity_rank_1_df = similarity_rank_df[similarity_rank_df['rank'] == 1]
    similarity_rank_2_df = similarity_rank_df[similarity_rank_df['rank'] == 2]
    similarity_rank_3_df = similarity_rank_df[similarity_rank_df['rank'] == 3]
    similarity_rank_4_df = similarity_rank_df[similarity_rank_df['rank'] == 4]
    similarity_rank_5_df = similarity_rank_df[similarity_rank_df['rank'] == 5]

    similarity_rank_1_df = similarity_rank_1_df.rename(columns={"similarity_rank": "similarity_rank_1"})
    similarity_rank_2_df = similarity_rank_2_df.rename(columns={"similarity_rank": "similarity_rank_2"})
    similarity_rank_3_df = similarity_rank_3_df.rename(columns={"similarity_rank": "similarity_rank_3"})
    similarity_rank_4_df = similarity_rank_4_df.rename(columns={"similarity_rank": "similarity_rank_4"})
    similarity_rank_5_df = similarity_rank_5_df.rename(columns={"similarity_rank": "similarity_rank_5"})
    
    #print(similarity_rank_1_df.sort_values('index'))
    #print(similarity_rank_2_df.sort_values('index'))
    neighbors_df = neighbors_df.reset_index()
    #print(neighbors_df)
    #print(len(neighbors_df))
    
    neighbors_df = pd.merge(neighbors_df, similarity_rank_1_df[['index', 'similarity_rank_1']], on='index')
    neighbors_df = pd.merge(neighbors_df, similarity_rank_2_df[['index', 'similarity_rank_2']], on='index')
    neighbors_df = pd.merge(neighbors_df, similarity_rank_3_df[['index', 'similarity_rank_3']], on='index')
    neighbors_df = pd.merge(neighbors_df, similarity_rank_4_df[['index', 'similarity_rank_4']], on='index')
    neighbors_df = pd.merge(neighbors_df, similarity_rank_5_df[['index', 'similarity_rank_5']], on='index')

    # print(neighbors_df[neighbors_df['player_id']==1629011])
    #print(len(neighbors_df))
    #print(neighbors_df.columns)

    sql_table = 'nearest_neighbors'
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    neighbors_df.to_sql(sql_table, con = engine, if_exists='replace', index=False)
    conn.close()

    
    # km = KMeans(n_clusters=5, random_state=0, n_init=10, algorithm='full')
    # y_km = km.fit_predict(X_scaled)
    #kg_predict = y_km.score(kmeans_df[0].iloc[0].to_numpy())
    #print(kg_predict)
    #print(y_km.cluster_centers_)

#calculate distortion for a range of number of cluster
    # distortions = []
    # for i in range(1, 20):
    #     km = KMeans(
    #         n_clusters=i, init='random',
    #         n_init=10, max_iter=300,
    #         tol=1e-04, random_state=0
    #     )
    #     km.fit(X_scaled)
    #     distortions.append(km.inertia_)

    # # plot
    # plt.plot(range(1, 20), distortions, marker='o')
    # plt.xlabel('Number of clusters')
    # plt.ylabel('Distortion')
    # plt.show()

    # plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y_km, s=50, cmap='viridis')

    # centers = km.cluster_centers_
    # plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
    # plt.show()

nearest_neighbors_df(clustering_df())
