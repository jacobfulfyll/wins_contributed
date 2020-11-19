import pandas as pd
import numpy as np
from sklearn import preprocessing
import psycopg2 as pg2
from sqlalchemy import create_engine
from time import sleep
from sklearn.decomposition import PCA




conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor() 

model_query = """SELECT *
                    FROM league_rosters
                    WHERE season_end = '2019';"""

all_stats_query = """SELECT COUNT(game_id) games_played, player_id, season_end,
       player_name, SUM(two_pt_score_uast) two_pt_score_uast, SUM(three_pt_score_uast) three_pt_score_uast,
       SUM(two_pt_score_ast) two_pt_score_ast, SUM(three_pt_score_ast) three_pt_score_ast, SUM(two_pt_score_uast_oreb) two_pt_score_uast_oreb,
       SUM(three_pt_score_uast_oreb) three_pt_score_uast_oreb, SUM(two_pt_score_ast_oreb) two_pt_score_ast_oreb,
       SUM(three_pt_score_ast_oreb) three_pt_score_ast_oreb, SUM(ast_2pt) ast_2pt, SUM(ast_3pt) ast_3pt, SUM(ast_two_pt_oreb) ast_two_pt_oreb,
       SUM(ast_three_pt_oreb) ast_three_pt_oreb, SUM(oreb_two_pt_uast) oreb_two_pt_uast, SUM(oreb_two_pt_ast) oreb_two_pt_ast,
       SUM(oreb_three_pt_uast) oreb_three_pt_uast, SUM(oreb_three_pt_ast) oreb_three_pt_ast, SUM(oreb_ft) oreb_ft, 
       SUM(dreb_blk) dreb_blk, SUM(dreb_no_blk) dreb_no_blk, SUM(to_score) to_score, SUM(stls_score) stls_score, 
       SUM(blks_score) blks_score, SUM(positive_ft) positive_ft, SUM(negative_ft) negative_ft, SUM(dfg_score) dfg_score,
       SUM(sast_score) sast_score, SUM(ft_ast_score) ft_ast_score, SUM(missed_two_pt_fg) missed_two_pt_fg,
       SUM(missed_three_pt_fg) missed_three_pt_fg, SUM(positive_def_fouls) positive_def_fouls,
       SUM(negative_def_fouls) negative_def_fouls
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end;"""

wins_contr_query = """SELECT player_id, season_end, player_name, SUM(value_contributed) wins_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        AND win_loss = 1
                        GROUP BY player_id, player_name, season_end;"""

val_contr_query = """SELECT player_id, season_end, player_name, SUM(value_contributed) total_val_contr, AVG(value_contributed) avg_val_contr
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end;"""

dd_query = """SELECT player_id, season_end, player_name, COUNT(game_id) games_played, SUM(discrepancy_total) total_discrepancy, AVG(depth_chart_rank) depth_rank
                        FROM all_seasons_discrepancy_depth
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_end;"""

age_exp_query = """SELECT *
                    FROM age_exp;"""

model_df = pd.read_sql(model_query, con=conn)
all_stats_df = pd.read_sql(all_stats_query, con=conn)
wins_contr_df = pd.read_sql(wins_contr_query, con=conn)
val_contr_df = pd.read_sql(val_contr_query, con=conn)
dd_df = pd.read_sql(dd_query, con=conn)
age_exp_df = pd.read_sql(age_exp_query, con=conn)

conn.close()


all_stats_df['abs_total_value'] = all_stats_df.iloc[:, 4:].sum(axis=1)
all_stats_df['id'] = [str(all_stats_df.loc[x, 'player_id']) + '_' + str(all_stats_df.loc[x, 'season_end']) for x in range(len(all_stats_df))]
model_df['id'] = [str(model_df.loc[x, 'player_id']) + '_' + str(model_df.loc[x, 'season_end']) for x in range(len(model_df))]
wins_contr_df['id'] = [str(wins_contr_df.loc[x, 'player_id']) + '_' + str(wins_contr_df.loc[x, 'season_end']) for x in range(len(wins_contr_df))]
dd_df['id'] = [str(dd_df.loc[x, 'player_id']) + '_' + str(dd_df.loc[x, 'season_end']) for x in range(len(dd_df))]

model_df = model_df.drop(columns=['team_name','age','exp'])
model_df['season_end'] = 2020
model_df['player_id'] = model_df['player_id'].astype(int)
model_df['team_id'] = model_df['team_id'].astype(int)
print(wins_contr_df.info())
print(model_df.info())

previous_wc_list = []
for idx in range(len(model_df)):
    try:
        previous_wc_list.append(wins_contr_df[(wins_contr_df['season_end'] == 2019 ) & (wins_contr_df['player_id'] == model_df.loc[idx, 'player_id'])].reset_index(drop=True).loc[0, 'wins_contr'])
    except:
        previous_wc_list.append(0)
model_df['wins_contr'] = previous_wc_list
print(model_df)

age_exp_df = age_exp_df[['player_id', 'season_end','age', 'exp']]
age_exp_df['season_end'] = age_exp_df['season_end'].astype(int)
age_exp_df['player_id'] = age_exp_df['player_id'].astype(int)

min_max_scaler = preprocessing.MinMaxScaler()
play_style_df = pd.DataFrame({'id':all_stats_df['id'], 'player_id':all_stats_df['player_id'], 'player_name':all_stats_df['player_name'], 'season_end':all_stats_df['season_end']})

for column in all_stats_df.columns[4:-2]:
    # play_style_df[column] = all_stats_df[column] / all_stats_df['abs_total_value']
    play_style_df[column] = min_max_scaler.fit_transform(all_stats_df[column].to_numpy().reshape(-1, 1))

for column in age_exp_df.columns[2:]:
    age_exp_df[column] = min_max_scaler.fit_transform(age_exp_df[column].to_numpy().reshape(-1, 1))

# dd_df['depth_rank_disc'] = dd_df['total_discrepancy'] / dd_df['depth_rank']
val_contr_df['total_vc'] = min_max_scaler.fit_transform(val_contr_df['total_val_contr'].to_numpy().reshape(-1, 1))
val_contr_df['avg_vc'] = min_max_scaler.fit_transform(val_contr_df['avg_val_contr'].to_numpy().reshape(-1, 1))
dd_df['games_played'] = min_max_scaler.fit_transform(dd_df['games_played'].to_numpy().reshape(-1, 1))
dd_df['depth_rank'] = min_max_scaler.fit_transform(dd_df['depth_rank'].to_numpy().reshape(-1, 1))
# dd_df['total_discrepancy'] = min_max_scaler.fit_transform(dd_df['total_discrepancy'].to_numpy().reshape(-1, 1))
# wins_contr_df['wins_contr'] = min_max_scaler.fit_transform(wins_contr_df['wins_contr'].to_numpy().reshape(-1, 1))

play_style_df = play_style_df.fillna(0)
style_X = play_style_df.iloc[:, 4:]

style_pca_model = PCA(n_components=10)
style_X_fit = style_pca_model.fit(style_X)
# print(style_X_fit.explained_variance_ratio_[0:20])
# print(style_X_fit.explained_variance_ratio_[0:10].sum())
style_X_transformed = style_X_fit.transform(style_X)
# print(style_X_transformed.shape)
previous_columns_list = play_style_df.columns
for idx, column in enumerate(play_style_df.columns):
    if idx > 3:
        play_style_df = play_style_df.drop(columns=column)
    else:
        pass

for idx in range(style_X_transformed.shape[1]):
    play_style_df[previous_columns_list[idx + 4]] = style_X_transformed[:, idx]
#print(play_style_df)

age_X = age_exp_df.iloc[:, 2:]
age_pca_model = PCA(n_components=1)
age_X_fit = age_pca_model.fit(age_X)
# print(age_X_fit.explained_variance_ratio_[0:20])
# print(age_X_fit.explained_variance_ratio_[0:10].sum())
age_X_transformed = age_X_fit.transform(age_X)
# print(X_transformed.shape)
age_exp_df['age_exp'] = age_X_transformed[:, 0]
age_exp_df = age_exp_df.drop(columns=['age', 'exp'])
# print(age_exp_df.info())



prediction_data_dict = {'two_pt_score_uast_1_t1':[], 'three_pt_score_uast_1_t1':[], 'two_pt_score_ast_1_t1':[], 'three_pt_score_ast_1_t1':[], 'two_pt_score_uast_oreb_1_t1':[], 'three_pt_score_uast_oreb_1_t1':[], 'two_pt_score_ast_oreb_1_t1':[], 'three_pt_score_ast_oreb_1_t1':[], 'ast_2pt_1_t1':[], 'ast_3pt_1_t1':[], 'ast_two_pt_oreb_1_t1':[], 'ast_three_pt_oreb_1_t1':[], 'oreb_two_pt_uast_1_t1':[], 'oreb_two_pt_ast_1_t1':[], 'oreb_three_pt_uast_1_t1':[], 'oreb_three_pt_ast_1_t1':[], 'oreb_ft_1_t1':[], 'dreb_blk_1_t1':[], 'dreb_no_blk_1_t1':[], 'to_score_1_t1':[], 'stls_score_1_t1':[], 'blks_score_1_t1':[], 'positive_ft_1_t1':[], 'negative_ft_1_t1':[], 'dfg_score_1_t1':[], 'sast_score_1_t1':[], 'ft_ast_score_1_t1':[], 'missed_two_pt_fg_1_t1':[], 'missed_three_pt_fg_1_t1':[], 'positive_def_fouls_1_t1':[], 'negative_def_fouls_1_t1':[],
'two_pt_score_uast_2_t1':[], 'three_pt_score_uast_2_t1':[], 'two_pt_score_ast_2_t1':[], 'three_pt_score_ast_2_t1':[], 'two_pt_score_uast_oreb_2_t1':[], 'three_pt_score_uast_oreb_2_t1':[], 'two_pt_score_ast_oreb_2_t1':[], 'three_pt_score_ast_oreb_2_t1':[], 'ast_2pt_2_t1':[], 'ast_3pt_2_t1':[], 'ast_two_pt_oreb_2_t1':[], 'ast_three_pt_oreb_2_t1':[], 'oreb_two_pt_uast_2_t1':[], 'oreb_two_pt_ast_2_t1':[], 'oreb_three_pt_uast_2_t1':[], 'oreb_three_pt_ast_2_t1':[], 'oreb_ft_2_t1':[], 'dreb_blk_2_t1':[], 'dreb_no_blk_2_t1':[], 'to_score_2_t1':[], 'stls_score_2_t1':[], 'blks_score_2_t1':[], 'positive_ft_2_t1':[], 'negative_ft_2_t1':[], 'dfg_score_2_t1':[], 'sast_score_2_t1':[], 'ft_ast_score_2_t1':[], 'missed_two_pt_fg_2_t1':[], 'missed_three_pt_fg_2_t1':[], 'positive_def_fouls_2_t1':[], 'negative_def_fouls_2_t1':[],
'two_pt_score_uast_3_t1':[], 'three_pt_score_uast_3_t1':[], 'two_pt_score_ast_3_t1':[], 'three_pt_score_ast_3_t1':[], 'two_pt_score_uast_oreb_3_t1':[], 'three_pt_score_uast_oreb_3_t1':[], 'two_pt_score_ast_oreb_3_t1':[], 'three_pt_score_ast_oreb_3_t1':[], 'ast_2pt_3_t1':[], 'ast_3pt_3_t1':[], 'ast_two_pt_oreb_3_t1':[], 'ast_three_pt_oreb_3_t1':[], 'oreb_two_pt_uast_3_t1':[], 'oreb_two_pt_ast_3_t1':[], 'oreb_three_pt_uast_3_t1':[], 'oreb_three_pt_ast_3_t1':[], 'oreb_ft_3_t1':[], 'dreb_blk_3_t1':[], 'dreb_no_blk_3_t1':[], 'to_score_3_t1':[], 'stls_score_3_t1':[], 'blks_score_3_t1':[], 'positive_ft_3_t1':[], 'negative_ft_3_t1':[], 'dfg_score_3_t1':[], 'sast_score_3_t1':[], 'ft_ast_score_3_t1':[], 'missed_two_pt_fg_3_t1':[], 'missed_three_pt_fg_3_t1':[], 'positive_def_fouls_3_t1':[], 'negative_def_fouls_3_t1':[],
'gp_1_t1':[],'vc_total_1_t1':[], 'depth_rank_1_t1':[], 'vc_avg_1_t1':[], 'age_exp_1_t1':[], 'gp_2_t1':[],'vc_total_2_t1':[], 'depth_rank_2_t1':[], 'vc_avg_2_t1':[], 'age_exp_2_t1':[], 'gp_3_t1':[],'vc_total_3_t1':[], 'depth_rank_3_t1':[], 'vc_avg_3_t1':[], 'age_exp_3_t1':[], 'two_pt_score_uast_1_t2':[], 'three_pt_score_uast_1_t2':[], 'two_pt_score_ast_1_t2':[], 'three_pt_score_ast_1_t2':[], 'two_pt_score_uast_oreb_1_t2':[], 'three_pt_score_uast_oreb_1_t2':[], 'two_pt_score_ast_oreb_1_t2':[], 'three_pt_score_ast_oreb_1_t2':[], 'ast_2pt_1_t2':[], 'ast_3pt_1_t2':[], 'ast_two_pt_oreb_1_t2':[], 'ast_three_pt_oreb_1_t2':[], 'oreb_two_pt_uast_1_t2':[], 'oreb_two_pt_ast_1_t2':[], 'oreb_three_pt_uast_1_t2':[], 'oreb_three_pt_ast_1_t2':[], 'oreb_ft_1_t2':[], 'dreb_blk_1_t2':[], 'dreb_no_blk_1_t2':[], 'to_score_1_t2':[], 'stls_score_1_t2':[], 'blks_score_1_t2':[], 'positive_ft_1_t2':[], 'negative_ft_1_t2':[], 'dfg_score_1_t2':[], 'sast_score_1_t2':[], 'ft_ast_score_1_t2':[], 'missed_two_pt_fg_1_t2':[], 'missed_three_pt_fg_1_t2':[], 'positive_def_fouls_1_t2':[], 'negative_def_fouls_1_t2':[],
'two_pt_score_uast_2_t2':[], 'three_pt_score_uast_2_t2':[], 'two_pt_score_ast_2_t2':[], 'three_pt_score_ast_2_t2':[], 'two_pt_score_uast_oreb_2_t2':[], 'three_pt_score_uast_oreb_2_t2':[], 'two_pt_score_ast_oreb_2_t2':[], 'three_pt_score_ast_oreb_2_t2':[], 'ast_2pt_2_t2':[], 'ast_3pt_2_t2':[], 'ast_two_pt_oreb_2_t2':[], 'ast_three_pt_oreb_2_t2':[], 'oreb_two_pt_uast_2_t2':[], 'oreb_two_pt_ast_2_t2':[], 'oreb_three_pt_uast_2_t2':[], 'oreb_three_pt_ast_2_t2':[], 'oreb_ft_2_t2':[], 'dreb_blk_2_t2':[], 'dreb_no_blk_2_t2':[], 'to_score_2_t2':[], 'stls_score_2_t2':[], 'blks_score_2_t2':[], 'positive_ft_2_t2':[], 'negative_ft_2_t2':[], 'dfg_score_2_t2':[], 'sast_score_2_t2':[], 'ft_ast_score_2_t2':[], 'missed_two_pt_fg_2_t2':[], 'missed_three_pt_fg_2_t2':[], 'positive_def_fouls_2_t2':[], 'negative_def_fouls_2_t2':[],
'two_pt_score_uast_3_t2':[], 'three_pt_score_uast_3_t2':[], 'two_pt_score_ast_3_t2':[], 'three_pt_score_ast_3_t2':[], 'two_pt_score_uast_oreb_3_t2':[], 'three_pt_score_uast_oreb_3_t2':[], 'two_pt_score_ast_oreb_3_t2':[], 'three_pt_score_ast_oreb_3_t2':[], 'ast_2pt_3_t2':[], 'ast_3pt_3_t2':[], 'ast_two_pt_oreb_3_t2':[], 'ast_three_pt_oreb_3_t2':[], 'oreb_two_pt_uast_3_t2':[], 'oreb_two_pt_ast_3_t2':[], 'oreb_three_pt_uast_3_t2':[], 'oreb_three_pt_ast_3_t2':[], 'oreb_ft_3_t2':[], 'dreb_blk_3_t2':[], 'dreb_no_blk_3_t2':[], 'to_score_3_t2':[], 'stls_score_3_t2':[], 'blks_score_3_t2':[], 'positive_ft_3_t2':[], 'negative_ft_3_t2':[], 'dfg_score_3_t2':[], 'sast_score_3_t2':[], 'ft_ast_score_3_t2':[], 'missed_two_pt_fg_3_t2':[], 'missed_three_pt_fg_3_t2':[], 'positive_def_fouls_3_t2':[], 'negative_def_fouls_3_t2':[],
'gp_1_t2':[],'vc_total_1_t2':[], 'depth_rank_1_t2':[], 'vc_avg_1_t2':[], 'age_exp_1_t2':[], 'gp_2_t2':[],'vc_total_2_t2':[], 'depth_rank_2_t2':[], 'vc_avg_2_t2':[], 'age_exp_2_t2':[], 'gp_3_t2':[],'vc_total_3_t2':[], 'depth_rank_3_t2':[], 'vc_avg_3_t2':[], 'age_exp_3_t2':[],'two_pt_score_uast_1_t3':[], 'three_pt_score_uast_1_t3':[], 'two_pt_score_ast_1_t3':[], 'three_pt_score_ast_1_t3':[], 'two_pt_score_uast_oreb_1_t3':[], 'three_pt_score_uast_oreb_1_t3':[], 'two_pt_score_ast_oreb_1_t3':[], 'three_pt_score_ast_oreb_1_t3':[], 'ast_2pt_1_t3':[], 'ast_3pt_1_t3':[], 'ast_two_pt_oreb_1_t3':[], 'ast_three_pt_oreb_1_t3':[], 'oreb_two_pt_uast_1_t3':[], 'oreb_two_pt_ast_1_t3':[], 'oreb_three_pt_uast_1_t3':[], 'oreb_three_pt_ast_1_t3':[], 'oreb_ft_1_t3':[], 'dreb_blk_1_t3':[], 'dreb_no_blk_1_t3':[], 'to_score_1_t3':[], 'stls_score_1_t3':[], 'blks_score_1_t3':[], 'positive_ft_1_t3':[], 'negative_ft_1_t3':[], 'dfg_score_1_t3':[], 'sast_score_1_t3':[], 'ft_ast_score_1_t3':[], 'missed_two_pt_fg_1_t3':[], 'missed_three_pt_fg_1_t3':[], 'positive_def_fouls_1_t3':[], 'negative_def_fouls_1_t3':[],
'two_pt_score_uast_2_t3':[], 'three_pt_score_uast_2_t3':[], 'two_pt_score_ast_2_t3':[], 'three_pt_score_ast_2_t3':[], 'two_pt_score_uast_oreb_2_t3':[], 'three_pt_score_uast_oreb_2_t3':[], 'two_pt_score_ast_oreb_2_t3':[], 'three_pt_score_ast_oreb_2_t3':[], 'ast_2pt_2_t3':[], 'ast_3pt_2_t3':[], 'ast_two_pt_oreb_2_t3':[], 'ast_three_pt_oreb_2_t3':[], 'oreb_two_pt_uast_2_t3':[], 'oreb_two_pt_ast_2_t3':[], 'oreb_three_pt_uast_2_t3':[], 'oreb_three_pt_ast_2_t3':[], 'oreb_ft_2_t3':[], 'dreb_blk_2_t3':[], 'dreb_no_blk_2_t3':[], 'to_score_2_t3':[], 'stls_score_2_t3':[], 'blks_score_2_t3':[], 'positive_ft_2_t3':[], 'negative_ft_2_t3':[], 'dfg_score_2_t3':[], 'sast_score_2_t3':[], 'ft_ast_score_2_t3':[], 'missed_two_pt_fg_2_t3':[], 'missed_three_pt_fg_2_t3':[], 'positive_def_fouls_2_t3':[], 'negative_def_fouls_2_t3':[],
'two_pt_score_uast_3_t3':[], 'three_pt_score_uast_3_t3':[], 'two_pt_score_ast_3_t3':[], 'three_pt_score_ast_3_t3':[], 'two_pt_score_uast_oreb_3_t3':[], 'three_pt_score_uast_oreb_3_t3':[], 'two_pt_score_ast_oreb_3_t3':[], 'three_pt_score_ast_oreb_3_t3':[], 'ast_2pt_3_t3':[], 'ast_3pt_3_t3':[], 'ast_two_pt_oreb_3_t3':[], 'ast_three_pt_oreb_3_t3':[], 'oreb_two_pt_uast_3_t3':[], 'oreb_two_pt_ast_3_t3':[], 'oreb_three_pt_uast_3_t3':[], 'oreb_three_pt_ast_3_t3':[], 'oreb_ft_3_t3':[], 'dreb_blk_3_t3':[], 'dreb_no_blk_3_t3':[], 'to_score_3_t3':[], 'stls_score_3_t3':[], 'blks_score_3_t3':[], 'positive_ft_3_t3':[], 'negative_ft_3_t3':[], 'dfg_score_3_t3':[], 'sast_score_3_t3':[], 'ft_ast_score_3_t3':[], 'missed_two_pt_fg_3_t3':[], 'missed_three_pt_fg_3_t3':[], 'positive_def_fouls_3_t3':[], 'negative_def_fouls_3_t3':[],
'gp_1_t3':[],'vc_total_1_t3':[], 'depth_rank_1_t3':[], 'vc_avg_1_t3':[], 'age_exp_1_t3':[], 'gp_2_t3':[],'vc_total_2_t3':[], 'depth_rank_2_t3':[], 'vc_avg_2_t3':[], 'age_exp_2_t3':[], 'gp_3_t3':[],'vc_total_3_t3':[], 'depth_rank_3_t3':[], 'vc_avg_3_t3':[], 'age_exp_3_t3':[],'two_pt_score_uast_1_t4':[], 'three_pt_score_uast_1_t4':[], 'two_pt_score_ast_1_t4':[], 'three_pt_score_ast_1_t4':[], 'two_pt_score_uast_oreb_1_t4':[], 'three_pt_score_uast_oreb_1_t4':[], 'two_pt_score_ast_oreb_1_t4':[], 'three_pt_score_ast_oreb_1_t4':[], 'ast_2pt_1_t4':[], 'ast_3pt_1_t4':[], 'ast_two_pt_oreb_1_t4':[], 'ast_three_pt_oreb_1_t4':[], 'oreb_two_pt_uast_1_t4':[], 'oreb_two_pt_ast_1_t4':[], 'oreb_three_pt_uast_1_t4':[], 'oreb_three_pt_ast_1_t4':[], 'oreb_ft_1_t4':[], 'dreb_blk_1_t4':[], 'dreb_no_blk_1_t4':[], 'to_score_1_t4':[], 'stls_score_1_t4':[], 'blks_score_1_t4':[], 'positive_ft_1_t4':[], 'negative_ft_1_t4':[], 'dfg_score_1_t4':[], 'sast_score_1_t4':[], 'ft_ast_score_1_t4':[], 'missed_two_pt_fg_1_t4':[], 'missed_three_pt_fg_1_t4':[], 'positive_def_fouls_1_t4':[], 'negative_def_fouls_1_t4':[],
'two_pt_score_uast_2_t4':[], 'three_pt_score_uast_2_t4':[], 'two_pt_score_ast_2_t4':[], 'three_pt_score_ast_2_t4':[], 'two_pt_score_uast_oreb_2_t4':[], 'three_pt_score_uast_oreb_2_t4':[], 'two_pt_score_ast_oreb_2_t4':[], 'three_pt_score_ast_oreb_2_t4':[], 'ast_2pt_2_t4':[], 'ast_3pt_2_t4':[], 'ast_two_pt_oreb_2_t4':[], 'ast_three_pt_oreb_2_t4':[], 'oreb_two_pt_uast_2_t4':[], 'oreb_two_pt_ast_2_t4':[], 'oreb_three_pt_uast_2_t4':[], 'oreb_three_pt_ast_2_t4':[], 'oreb_ft_2_t4':[], 'dreb_blk_2_t4':[], 'dreb_no_blk_2_t4':[], 'to_score_2_t4':[], 'stls_score_2_t4':[], 'blks_score_2_t4':[], 'positive_ft_2_t4':[], 'negative_ft_2_t4':[], 'dfg_score_2_t4':[], 'sast_score_2_t4':[], 'ft_ast_score_2_t4':[], 'missed_two_pt_fg_2_t4':[], 'missed_three_pt_fg_2_t4':[], 'positive_def_fouls_2_t4':[], 'negative_def_fouls_2_t4':[],
'two_pt_score_uast_3_t4':[], 'three_pt_score_uast_3_t4':[], 'two_pt_score_ast_3_t4':[], 'three_pt_score_ast_3_t4':[], 'two_pt_score_uast_oreb_3_t4':[], 'three_pt_score_uast_oreb_3_t4':[], 'two_pt_score_ast_oreb_3_t4':[], 'three_pt_score_ast_oreb_3_t4':[], 'ast_2pt_3_t4':[], 'ast_3pt_3_t4':[], 'ast_two_pt_oreb_3_t4':[], 'ast_three_pt_oreb_3_t4':[], 'oreb_two_pt_uast_3_t4':[], 'oreb_two_pt_ast_3_t4':[], 'oreb_three_pt_uast_3_t4':[], 'oreb_three_pt_ast_3_t4':[], 'oreb_ft_3_t4':[], 'dreb_blk_3_t4':[], 'dreb_no_blk_3_t4':[], 'to_score_3_t4':[], 'stls_score_3_t4':[], 'blks_score_3_t4':[], 'positive_ft_3_t4':[], 'negative_ft_3_t4':[], 'dfg_score_3_t4':[], 'sast_score_3_t4':[], 'ft_ast_score_3_t4':[], 'missed_two_pt_fg_3_t4':[], 'missed_three_pt_fg_3_t4':[], 'positive_def_fouls_3_t4':[], 'negative_def_fouls_3_t4':[],
'gp_1_t4':[],'vc_total_1_t4':[], 'depth_rank_1_t4':[], 'vc_avg_1_t4':[], 'age_exp_1_t4':[], 'gp_2_t4':[],'vc_total_2_t4':[], 'depth_rank_2_t4':[], 'vc_avg_2_t4':[], 'age_exp_2_t4':[], 'gp_3_t4':[],'vc_total_3_t4':[], 'depth_rank_3_t4':[], 'vc_avg_3_t4':[], 'age_exp_3_t4':[],'two_pt_score_uast_1_t5':[], 'three_pt_score_uast_1_t5':[], 'two_pt_score_ast_1_t5':[], 'three_pt_score_ast_1_t5':[], 'two_pt_score_uast_oreb_1_t5':[], 'three_pt_score_uast_oreb_1_t5':[], 'two_pt_score_ast_oreb_1_t5':[], 'three_pt_score_ast_oreb_1_t5':[], 'ast_2pt_1_t5':[], 'ast_3pt_1_t5':[], 'ast_two_pt_oreb_1_t5':[], 'ast_three_pt_oreb_1_t5':[], 'oreb_two_pt_uast_1_t5':[], 'oreb_two_pt_ast_1_t5':[], 'oreb_three_pt_uast_1_t5':[], 'oreb_three_pt_ast_1_t5':[], 'oreb_ft_1_t5':[], 'dreb_blk_1_t5':[], 'dreb_no_blk_1_t5':[], 'to_score_1_t5':[], 'stls_score_1_t5':[], 'blks_score_1_t5':[], 'positive_ft_1_t5':[], 'negative_ft_1_t5':[], 'dfg_score_1_t5':[], 'sast_score_1_t5':[], 'ft_ast_score_1_t5':[], 'missed_two_pt_fg_1_t5':[], 'missed_three_pt_fg_1_t5':[], 'positive_def_fouls_1_t5':[], 'negative_def_fouls_1_t5':[],
'two_pt_score_uast_2_t5':[], 'three_pt_score_uast_2_t5':[], 'two_pt_score_ast_2_t5':[], 'three_pt_score_ast_2_t5':[], 'two_pt_score_uast_oreb_2_t5':[], 'three_pt_score_uast_oreb_2_t5':[], 'two_pt_score_ast_oreb_2_t5':[], 'three_pt_score_ast_oreb_2_t5':[], 'ast_2pt_2_t5':[], 'ast_3pt_2_t5':[], 'ast_two_pt_oreb_2_t5':[], 'ast_three_pt_oreb_2_t5':[], 'oreb_two_pt_uast_2_t5':[], 'oreb_two_pt_ast_2_t5':[], 'oreb_three_pt_uast_2_t5':[], 'oreb_three_pt_ast_2_t5':[], 'oreb_ft_2_t5':[], 'dreb_blk_2_t5':[], 'dreb_no_blk_2_t5':[], 'to_score_2_t5':[], 'stls_score_2_t5':[], 'blks_score_2_t5':[], 'positive_ft_2_t5':[], 'negative_ft_2_t5':[], 'dfg_score_2_t5':[], 'sast_score_2_t5':[], 'ft_ast_score_2_t5':[], 'missed_two_pt_fg_2_t5':[], 'missed_three_pt_fg_2_t5':[], 'positive_def_fouls_2_t5':[], 'negative_def_fouls_2_t5':[],
'two_pt_score_uast_3_t5':[], 'three_pt_score_uast_3_t5':[], 'two_pt_score_ast_3_t5':[], 'three_pt_score_ast_3_t5':[], 'two_pt_score_uast_oreb_3_t5':[], 'three_pt_score_uast_oreb_3_t5':[], 'two_pt_score_ast_oreb_3_t5':[], 'three_pt_score_ast_oreb_3_t5':[], 'ast_2pt_3_t5':[], 'ast_3pt_3_t5':[], 'ast_two_pt_oreb_3_t5':[], 'ast_three_pt_oreb_3_t5':[], 'oreb_two_pt_uast_3_t5':[], 'oreb_two_pt_ast_3_t5':[], 'oreb_three_pt_uast_3_t5':[], 'oreb_three_pt_ast_3_t5':[], 'oreb_ft_3_t5':[], 'dreb_blk_3_t5':[], 'dreb_no_blk_3_t5':[], 'to_score_3_t5':[], 'stls_score_3_t5':[], 'blks_score_3_t5':[], 'positive_ft_3_t5':[], 'negative_ft_3_t5':[], 'dfg_score_3_t5':[], 'sast_score_3_t5':[], 'ft_ast_score_3_t5':[], 'missed_two_pt_fg_3_t5':[], 'missed_three_pt_fg_3_t5':[], 'positive_def_fouls_3_t5':[], 'negative_def_fouls_3_t5':[],
'gp_1_t5':[],'vc_total_1_t5':[], 'depth_rank_1_t5':[], 'vc_avg_1_t5':[], 'age_exp_1_t5':[], 'gp_2_t5':[],'vc_total_2_t5':[], 'depth_rank_2_t5':[], 'vc_avg_2_t5':[], 'age_exp_2_t5':[], 'gp_3_t5':[],'vc_total_3_t5':[], 'depth_rank_3_t5':[], 'vc_avg_3_t5':[], 'age_exp_3_t5':[],'two_pt_score_uast_1_t6':[], 'three_pt_score_uast_1_t6':[], 'two_pt_score_ast_1_t6':[], 'three_pt_score_ast_1_t6':[], 'two_pt_score_uast_oreb_1_t6':[], 'three_pt_score_uast_oreb_1_t6':[], 'two_pt_score_ast_oreb_1_t6':[], 'three_pt_score_ast_oreb_1_t6':[], 'ast_2pt_1_t6':[], 'ast_3pt_1_t6':[], 'ast_two_pt_oreb_1_t6':[], 'ast_three_pt_oreb_1_t6':[], 'oreb_two_pt_uast_1_t6':[], 'oreb_two_pt_ast_1_t6':[], 'oreb_three_pt_uast_1_t6':[], 'oreb_three_pt_ast_1_t6':[], 'oreb_ft_1_t6':[], 'dreb_blk_1_t6':[], 'dreb_no_blk_1_t6':[], 'to_score_1_t6':[], 'stls_score_1_t6':[], 'blks_score_1_t6':[], 'positive_ft_1_t6':[], 'negative_ft_1_t6':[], 'dfg_score_1_t6':[], 'sast_score_1_t6':[], 'ft_ast_score_1_t6':[], 'missed_two_pt_fg_1_t6':[], 'missed_three_pt_fg_1_t6':[], 'positive_def_fouls_1_t6':[], 'negative_def_fouls_1_t6':[],
'two_pt_score_uast_2_t6':[], 'three_pt_score_uast_2_t6':[], 'two_pt_score_ast_2_t6':[], 'three_pt_score_ast_2_t6':[], 'two_pt_score_uast_oreb_2_t6':[], 'three_pt_score_uast_oreb_2_t6':[], 'two_pt_score_ast_oreb_2_t6':[], 'three_pt_score_ast_oreb_2_t6':[], 'ast_2pt_2_t6':[], 'ast_3pt_2_t6':[], 'ast_two_pt_oreb_2_t6':[], 'ast_three_pt_oreb_2_t6':[], 'oreb_two_pt_uast_2_t6':[], 'oreb_two_pt_ast_2_t6':[], 'oreb_three_pt_uast_2_t6':[], 'oreb_three_pt_ast_2_t6':[], 'oreb_ft_2_t6':[], 'dreb_blk_2_t6':[], 'dreb_no_blk_2_t6':[], 'to_score_2_t6':[], 'stls_score_2_t6':[], 'blks_score_2_t6':[], 'positive_ft_2_t6':[], 'negative_ft_2_t6':[], 'dfg_score_2_t6':[], 'sast_score_2_t6':[], 'ft_ast_score_2_t6':[], 'missed_two_pt_fg_2_t6':[], 'missed_three_pt_fg_2_t6':[], 'positive_def_fouls_2_t6':[], 'negative_def_fouls_2_t6':[],
'two_pt_score_uast_3_t6':[], 'three_pt_score_uast_3_t6':[], 'two_pt_score_ast_3_t6':[], 'three_pt_score_ast_3_t6':[], 'two_pt_score_uast_oreb_3_t6':[], 'three_pt_score_uast_oreb_3_t6':[], 'two_pt_score_ast_oreb_3_t6':[], 'three_pt_score_ast_oreb_3_t6':[], 'ast_2pt_3_t6':[], 'ast_3pt_3_t6':[], 'ast_two_pt_oreb_3_t6':[], 'ast_three_pt_oreb_3_t6':[], 'oreb_two_pt_uast_3_t6':[], 'oreb_two_pt_ast_3_t6':[], 'oreb_three_pt_uast_3_t6':[], 'oreb_three_pt_ast_3_t6':[], 'oreb_ft_3_t6':[], 'dreb_blk_3_t6':[], 'dreb_no_blk_3_t6':[], 'to_score_3_t6':[], 'stls_score_3_t6':[], 'blks_score_3_t6':[], 'positive_ft_3_t6':[], 'negative_ft_3_t6':[], 'dfg_score_3_t6':[], 'sast_score_3_t6':[], 'ft_ast_score_3_t6':[], 'missed_two_pt_fg_3_t6':[], 'missed_three_pt_fg_3_t6':[], 'positive_def_fouls_3_t6':[], 'negative_def_fouls_3_t6':[],
'gp_1_t6':[],'vc_total_1_t6':[], 'depth_rank_1_t6':[], 'vc_avg_1_t6':[], 'age_exp_1_t6':[], 'gp_2_t6':[],'vc_total_2_t6':[], 'depth_rank_2_t6':[], 'vc_avg_2_t6':[], 'age_exp_2_t6':[], 'gp_3_t6':[],'vc_total_3_t6':[], 'depth_rank_3_t6':[], 'vc_avg_3_t6':[], 'age_exp_3_t6':[],'two_pt_score_uast_1_t7':[], 'three_pt_score_uast_1_t7':[], 'two_pt_score_ast_1_t7':[], 'three_pt_score_ast_1_t7':[], 'two_pt_score_uast_oreb_1_t7':[], 'three_pt_score_uast_oreb_1_t7':[], 'two_pt_score_ast_oreb_1_t7':[], 'three_pt_score_ast_oreb_1_t7':[], 'ast_2pt_1_t7':[], 'ast_3pt_1_t7':[], 'ast_two_pt_oreb_1_t7':[], 'ast_three_pt_oreb_1_t7':[], 'oreb_two_pt_uast_1_t7':[], 'oreb_two_pt_ast_1_t7':[], 'oreb_three_pt_uast_1_t7':[], 'oreb_three_pt_ast_1_t7':[], 'oreb_ft_1_t7':[], 'dreb_blk_1_t7':[], 'dreb_no_blk_1_t7':[], 'to_score_1_t7':[], 'stls_score_1_t7':[], 'blks_score_1_t7':[], 'positive_ft_1_t7':[], 'negative_ft_1_t7':[], 'dfg_score_1_t7':[], 'sast_score_1_t7':[], 'ft_ast_score_1_t7':[], 'missed_two_pt_fg_1_t7':[], 'missed_three_pt_fg_1_t7':[], 'positive_def_fouls_1_t7':[], 'negative_def_fouls_1_t7':[],
'two_pt_score_uast_2_t7':[], 'three_pt_score_uast_2_t7':[], 'two_pt_score_ast_2_t7':[], 'three_pt_score_ast_2_t7':[], 'two_pt_score_uast_oreb_2_t7':[], 'three_pt_score_uast_oreb_2_t7':[], 'two_pt_score_ast_oreb_2_t7':[], 'three_pt_score_ast_oreb_2_t7':[], 'ast_2pt_2_t7':[], 'ast_3pt_2_t7':[], 'ast_two_pt_oreb_2_t7':[], 'ast_three_pt_oreb_2_t7':[], 'oreb_two_pt_uast_2_t7':[], 'oreb_two_pt_ast_2_t7':[], 'oreb_three_pt_uast_2_t7':[], 'oreb_three_pt_ast_2_t7':[], 'oreb_ft_2_t7':[], 'dreb_blk_2_t7':[], 'dreb_no_blk_2_t7':[], 'to_score_2_t7':[], 'stls_score_2_t7':[], 'blks_score_2_t7':[], 'positive_ft_2_t7':[], 'negative_ft_2_t7':[], 'dfg_score_2_t7':[], 'sast_score_2_t7':[], 'ft_ast_score_2_t7':[], 'missed_two_pt_fg_2_t7':[], 'missed_three_pt_fg_2_t7':[], 'positive_def_fouls_2_t7':[], 'negative_def_fouls_2_t7':[],
'two_pt_score_uast_3_t7':[], 'three_pt_score_uast_3_t7':[], 'two_pt_score_ast_3_t7':[], 'three_pt_score_ast_3_t7':[], 'two_pt_score_uast_oreb_3_t7':[], 'three_pt_score_uast_oreb_3_t7':[], 'two_pt_score_ast_oreb_3_t7':[], 'three_pt_score_ast_oreb_3_t7':[], 'ast_2pt_3_t7':[], 'ast_3pt_3_t7':[], 'ast_two_pt_oreb_3_t7':[], 'ast_three_pt_oreb_3_t7':[], 'oreb_two_pt_uast_3_t7':[], 'oreb_two_pt_ast_3_t7':[], 'oreb_three_pt_uast_3_t7':[], 'oreb_three_pt_ast_3_t7':[], 'oreb_ft_3_t7':[], 'dreb_blk_3_t7':[], 'dreb_no_blk_3_t7':[], 'to_score_3_t7':[], 'stls_score_3_t7':[], 'blks_score_3_t7':[], 'positive_ft_3_t7':[], 'negative_ft_3_t7':[], 'dfg_score_3_t7':[], 'sast_score_3_t7':[], 'ft_ast_score_3_t7':[], 'missed_two_pt_fg_3_t7':[], 'missed_three_pt_fg_3_t7':[], 'positive_def_fouls_3_t7':[], 'negative_def_fouls_3_t7':[],
'gp_1_t7':[],'vc_total_1_t7':[], 'depth_rank_1_t7':[], 'vc_avg_1_t7':[], 'age_exp_1_t7':[], 'gp_2_t7':[],'vc_total_2_t7':[], 'depth_rank_2_t7':[], 'vc_avg_2_t7':[], 'age_exp_2_t7':[], 'gp_3_t7':[],'vc_total_3_t7':[], 'depth_rank_3_t7':[], 'vc_avg_3_t7':[], 'age_exp_3_t7':[],'two_pt_score_uast_1_t8':[], 'three_pt_score_uast_1_t8':[], 'two_pt_score_ast_1_t8':[], 'three_pt_score_ast_1_t8':[], 'two_pt_score_uast_oreb_1_t8':[], 'three_pt_score_uast_oreb_1_t8':[], 'two_pt_score_ast_oreb_1_t8':[], 'three_pt_score_ast_oreb_1_t8':[], 'ast_2pt_1_t8':[], 'ast_3pt_1_t8':[], 'ast_two_pt_oreb_1_t8':[], 'ast_three_pt_oreb_1_t8':[], 'oreb_two_pt_uast_1_t8':[], 'oreb_two_pt_ast_1_t8':[], 'oreb_three_pt_uast_1_t8':[], 'oreb_three_pt_ast_1_t8':[], 'oreb_ft_1_t8':[], 'dreb_blk_1_t8':[], 'dreb_no_blk_1_t8':[], 'to_score_1_t8':[], 'stls_score_1_t8':[], 'blks_score_1_t8':[], 'positive_ft_1_t8':[], 'negative_ft_1_t8':[], 'dfg_score_1_t8':[], 'sast_score_1_t8':[], 'ft_ast_score_1_t8':[], 'missed_two_pt_fg_1_t8':[], 'missed_three_pt_fg_1_t8':[], 'positive_def_fouls_1_t8':[], 'negative_def_fouls_1_t8':[],
'two_pt_score_uast_2_t8':[], 'three_pt_score_uast_2_t8':[], 'two_pt_score_ast_2_t8':[], 'three_pt_score_ast_2_t8':[], 'two_pt_score_uast_oreb_2_t8':[], 'three_pt_score_uast_oreb_2_t8':[], 'two_pt_score_ast_oreb_2_t8':[], 'three_pt_score_ast_oreb_2_t8':[], 'ast_2pt_2_t8':[], 'ast_3pt_2_t8':[], 'ast_two_pt_oreb_2_t8':[], 'ast_three_pt_oreb_2_t8':[], 'oreb_two_pt_uast_2_t8':[], 'oreb_two_pt_ast_2_t8':[], 'oreb_three_pt_uast_2_t8':[], 'oreb_three_pt_ast_2_t8':[], 'oreb_ft_2_t8':[], 'dreb_blk_2_t8':[], 'dreb_no_blk_2_t8':[], 'to_score_2_t8':[], 'stls_score_2_t8':[], 'blks_score_2_t8':[], 'positive_ft_2_t8':[], 'negative_ft_2_t8':[], 'dfg_score_2_t8':[], 'sast_score_2_t8':[], 'ft_ast_score_2_t8':[], 'missed_two_pt_fg_2_t8':[], 'missed_three_pt_fg_2_t8':[], 'positive_def_fouls_2_t8':[], 'negative_def_fouls_2_t8':[],
'two_pt_score_uast_3_t8':[], 'three_pt_score_uast_3_t8':[], 'two_pt_score_ast_3_t8':[], 'three_pt_score_ast_3_t8':[], 'two_pt_score_uast_oreb_3_t8':[], 'three_pt_score_uast_oreb_3_t8':[], 'two_pt_score_ast_oreb_3_t8':[], 'three_pt_score_ast_oreb_3_t8':[], 'ast_2pt_3_t8':[], 'ast_3pt_3_t8':[], 'ast_two_pt_oreb_3_t8':[], 'ast_three_pt_oreb_3_t8':[], 'oreb_two_pt_uast_3_t8':[], 'oreb_two_pt_ast_3_t8':[], 'oreb_three_pt_uast_3_t8':[], 'oreb_three_pt_ast_3_t8':[], 'oreb_ft_3_t8':[], 'dreb_blk_3_t8':[], 'dreb_no_blk_3_t8':[], 'to_score_3_t8':[], 'stls_score_3_t8':[], 'blks_score_3_t8':[], 'positive_ft_3_t8':[], 'negative_ft_3_t8':[], 'dfg_score_3_t8':[], 'sast_score_3_t8':[], 'ft_ast_score_3_t8':[], 'missed_two_pt_fg_3_t8':[], 'missed_three_pt_fg_3_t8':[], 'positive_def_fouls_3_t8':[], 'negative_def_fouls_3_t8':[],
'gp_1_t8':[],'vc_total_1_t8':[], 'depth_rank_1_t8':[], 'vc_avg_1_t8':[], 'age_exp_1_t8':[], 'gp_2_t8':[],'vc_total_2_t8':[], 'depth_rank_2_t8':[], 'vc_avg_2_t8':[], 'age_exp_2_t8':[], 'gp_3_t8':[],'vc_total_3_t8':[], 'depth_rank_3_t8':[], 'vc_avg_3_t8':[], 'age_exp_3_t8':[],'two_pt_score_uast_1_t9':[], 'three_pt_score_uast_1_t9':[], 'two_pt_score_ast_1_t9':[], 'three_pt_score_ast_1_t9':[], 'two_pt_score_uast_oreb_1_t9':[], 'three_pt_score_uast_oreb_1_t9':[], 'two_pt_score_ast_oreb_1_t9':[], 'three_pt_score_ast_oreb_1_t9':[], 'ast_2pt_1_t9':[], 'ast_3pt_1_t9':[], 'ast_two_pt_oreb_1_t9':[], 'ast_three_pt_oreb_1_t9':[], 'oreb_two_pt_uast_1_t9':[], 'oreb_two_pt_ast_1_t9':[], 'oreb_three_pt_uast_1_t9':[], 'oreb_three_pt_ast_1_t9':[], 'oreb_ft_1_t9':[], 'dreb_blk_1_t9':[], 'dreb_no_blk_1_t9':[], 'to_score_1_t9':[], 'stls_score_1_t9':[], 'blks_score_1_t9':[], 'positive_ft_1_t9':[], 'negative_ft_1_t9':[], 'dfg_score_1_t9':[], 'sast_score_1_t9':[], 'ft_ast_score_1_t9':[], 'missed_two_pt_fg_1_t9':[], 'missed_three_pt_fg_1_t9':[], 'positive_def_fouls_1_t9':[], 'negative_def_fouls_1_t9':[],
'two_pt_score_uast_2_t9':[], 'three_pt_score_uast_2_t9':[], 'two_pt_score_ast_2_t9':[], 'three_pt_score_ast_2_t9':[], 'two_pt_score_uast_oreb_2_t9':[], 'three_pt_score_uast_oreb_2_t9':[], 'two_pt_score_ast_oreb_2_t9':[], 'three_pt_score_ast_oreb_2_t9':[], 'ast_2pt_2_t9':[], 'ast_3pt_2_t9':[], 'ast_two_pt_oreb_2_t9':[], 'ast_three_pt_oreb_2_t9':[], 'oreb_two_pt_uast_2_t9':[], 'oreb_two_pt_ast_2_t9':[], 'oreb_three_pt_uast_2_t9':[], 'oreb_three_pt_ast_2_t9':[], 'oreb_ft_2_t9':[], 'dreb_blk_2_t9':[], 'dreb_no_blk_2_t9':[], 'to_score_2_t9':[], 'stls_score_2_t9':[], 'blks_score_2_t9':[], 'positive_ft_2_t9':[], 'negative_ft_2_t9':[], 'dfg_score_2_t9':[], 'sast_score_2_t9':[], 'ft_ast_score_2_t9':[], 'missed_two_pt_fg_2_t9':[], 'missed_three_pt_fg_2_t9':[], 'positive_def_fouls_2_t9':[], 'negative_def_fouls_2_t9':[],
'two_pt_score_uast_3_t9':[], 'three_pt_score_uast_3_t9':[], 'two_pt_score_ast_3_t9':[], 'three_pt_score_ast_3_t9':[], 'two_pt_score_uast_oreb_3_t9':[], 'three_pt_score_uast_oreb_3_t9':[], 'two_pt_score_ast_oreb_3_t9':[], 'three_pt_score_ast_oreb_3_t9':[], 'ast_2pt_3_t9':[], 'ast_3pt_3_t9':[], 'ast_two_pt_oreb_3_t9':[], 'ast_three_pt_oreb_3_t9':[], 'oreb_two_pt_uast_3_t9':[], 'oreb_two_pt_ast_3_t9':[], 'oreb_three_pt_uast_3_t9':[], 'oreb_three_pt_ast_3_t9':[], 'oreb_ft_3_t9':[], 'dreb_blk_3_t9':[], 'dreb_no_blk_3_t9':[], 'to_score_3_t9':[], 'stls_score_3_t9':[], 'blks_score_3_t9':[], 'positive_ft_3_t9':[], 'negative_ft_3_t9':[], 'dfg_score_3_t9':[], 'sast_score_3_t9':[], 'ft_ast_score_3_t9':[], 'missed_two_pt_fg_3_t9':[], 'missed_three_pt_fg_3_t9':[], 'positive_def_fouls_3_t9':[], 'negative_def_fouls_3_t9':[],
'gp_1_t9':[],'vc_total_1_t9':[], 'depth_rank_1_t9':[], 'vc_avg_1_t9':[], 'age_exp_1_t9':[], 'gp_2_t9':[],'vc_total_2_t9':[], 'depth_rank_2_t9':[], 'vc_avg_2_t9':[], 'age_exp_2_t9':[], 'gp_3_t9':[],'vc_total_3_t9':[], 'depth_rank_3_t9':[], 'vc_avg_3_t9':[], 'age_exp_3_t9':[]}

for idx in range(len(model_df)):
    print(str(idx) + ' / ' + str(len(model_df)))
    current_season = model_df.loc[idx, 'season_end']
    #print('CURRENT_SEASON: ' + str(current_season)) 
    teammates_df = model_df[model_df['team_id'] == model_df.loc[idx, 'team_id']]
    teammates_df = teammates_df.sort_values('wins_contr', ascending=False).reset_index(drop=True)
    #print(teammates_df)

    player_id_list = [model_df.loc[idx, 'player_id']]
    counter = 1
    teammate = 1
    # print(teammates_df)
    while teammate <= 8:
        # print(player_id_list)
        # if teammates_df.loc[counter, 'player_id'] == model_df.loc[idx, 'player_id']:
        #     counter += 1
        # else:
        player_id_list.append(teammates_df.loc[counter, 'player_id'])
        teammate += 1
        counter += 1
    for teammate_num, current_player_id in enumerate(player_id_list):
        for year_count in range(3):
            for column in play_style_df.columns[4:]:
                try:
                    style_variable = play_style_df[(play_style_df['player_id'] == current_player_id) & (play_style_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, column]
                except:
                    style_variable = 0
                style_key = column + '_' + str(year_count + 1) + '_t' + str(teammate_num + 1)
                prediction_data_dict[style_key].append(style_variable)     
        
            try:
                prediction_data_dict['gp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(dd_df[(dd_df['player_id'] == current_player_id) & (dd_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, 'games_played'])   
            except:
                prediction_data_dict['gp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(0)
            try:
                prediction_data_dict['depth_rank_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(dd_df[(dd_df['player_id'] == current_player_id) & (dd_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, 'depth_rank'])
            except:
                prediction_data_dict['depth_rank_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(0)
            try:
                prediction_data_dict['age_exp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(age_exp_df[(age_exp_df['player_id'] == current_player_id) & (age_exp_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, 'age_exp'])
            except:
                prediction_data_dict['age_exp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(0)
            try:
                prediction_data_dict['vc_avg_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(val_contr_df[(val_contr_df['player_id'] == current_player_id) & (val_contr_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, 'avg_vc'])
            except:
                prediction_data_dict['vc_avg_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(0) 
            try:
                prediction_data_dict['vc_total_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(val_contr_df[(val_contr_df['player_id'] == current_player_id) & (val_contr_df['season_end'] == current_season - year_count - 1)].reset_index(drop=True).loc[0, 'total_vc'])
            except:
                prediction_data_dict['vc_total_' + str(year_count + 1) + '_t' + str(teammate_num + 1)].append(0) 


    # print(prediction_data_dict)
    # sleep(10)



for teammate_num in range(9):
    for year_count in range(3):
        for idx in range(len(play_style_df.columns[4:])):
            print(idx)
            style_column_name = play_style_df.columns[idx + 4] + '_' + str(year_count + 1) + '_t' + str(teammate_num + 1)
            model_df[style_column_name] = prediction_data_dict[style_column_name]

        model_df['gp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)] = prediction_data_dict['gp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)]
        model_df['depth_rank_' + str(year_count + 1) + '_t' + str(teammate_num + 1)] = prediction_data_dict['depth_rank_' + str(year_count + 1) + '_t' + str(teammate_num + 1)]
        model_df['age_exp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)] = prediction_data_dict['age_exp_' + str(year_count + 1) + '_t' + str(teammate_num + 1)]
        # model_df['discrepancy_' + str(year_count + 1) + '_t' + str(teammate_num + 1)] = prediction_data_dict['discrepancy_' + str(year_count + 1) + '_t' + str(teammate_num + 1)]
        # model_df['wc_' + str(year_count + 1) + '_t' + str(teammate_num + 1)] = prediction_data_dict['wc_' + str(year_count + 1) + '_t' + str(teammate_num + 1)]

print(model_df)



conn = pg2.connect(dbname = 'postgres', host = "localhost")
conn.autocommit = True
engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
model_df.to_sql('predicition_data_wc_2020_season', con = engine, if_exists= "replace", index=False)
conn.close()

