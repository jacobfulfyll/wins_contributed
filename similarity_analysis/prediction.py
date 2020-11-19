import psycopg2 as pg2
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import sys
sys.path.append("..")
from player_prediction import grid_search
from sklearn import preprocessing



conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

full_data_query = """SELECT *
                        FROM prediction_data_wc;"""

predict_2020_query = """SELECT *
                        FROM predicition_data_wc_2020_season"""


full_data_df = pd.read_sql(full_data_query, con=conn)
full_data_df = full_data_df.fillna(0)

predict_2020_df = pd.read_sql(predict_2020_query, con=conn)
predict_2020_df = predict_2020_df.fillna(0)

conn.close()

# print(predict_2020_df)
# print(predict_2020_df[predict_2020_df['player_name'] == 'James Harden'].iloc[:, 3:10])
# print(predict_2020_df[predict_2020_df['player_name'] == 'James Harden'].iloc[:, 10:20])
# print(predict_2020_df[predict_2020_df['player_name'] == 'James Harden'].iloc[:, 20:30])
# print(predict_2020_df[predict_2020_df['player_name'] == 'James Harden'].iloc[:, 30:40])
# print(predict_2020_df[predict_2020_df['player_name'] == 'James Harden'].iloc[:, 40:])
# print(predict_2020_df[predict_2020_df['player_name'] == 'DeMarcus Cousins'].iloc[:, 3:10])
# print(predict_2020_df[predict_2020_df['player_name'] == 'DeMarcus Cousins'].iloc[:, 10:20])
# print(predict_2020_df[predict_2020_df['player_name'] == 'DeMarcus Cousins'].iloc[:, 20:30])
# print(predict_2020_df[predict_2020_df['player_name'] == 'DeMarcus Cousins'].iloc[:, 30:40])
# print(predict_2020_df[predict_2020_df['player_name'] == 'DeMarcus Cousins'].iloc[:, 40:])
# print(full_data_df[full_data_df['player_name'] == 'Chimezie Metu'])

# print(full_data_df.iloc[:, 5])


# print(full_data_df.iloc[:, 6:])

min_max_scaler = preprocessing.MinMaxScaler()

X_predict = predict_2020_df.iloc[:, 6:].to_numpy()
# X_predict = min_max_scaler.fit_transform(X_predict)

X_predict_details = predict_2020_df.iloc[:, 3]

X_train = full_data_df.iloc[:, 6:].to_numpy()
print(X_train.shape)
# X_train = min_max_scaler.fit_transform(X_train)
# X_train = full_data_df.iloc[:, [1,3]]
# pca_list = [X_train, X_predict]
# print(X_wins)
# print(X)

# print(X_train.shape)
# print(X_predict.shape)

n_components = 20
pca_model_1 = PCA(n_components=n_components)
pca_model_2 = PCA(n_components=n_components)
X_train_fit = pca_model_1.fit(X_train)
X_train = pca_model_1.fit_transform(X_train)
X_predict = pca_model_2.fit_transform(X_predict)
print(X_predict.shape)
print(X_train.shape)
print(X_train_fit.explained_variance_ratio_[0:30])
print(X_train_fit.explained_variance_ratio_[0:40].sum())

# for idx, data in enumerate(pca_list):
#     pca_model = PCA(n_components=n_components)
#     X_fit = pca_model.fit(data)
#     print(X_fit.explained_variance_ratio_[0:60])
#     print(X_fit.explained_variance_ratio_[0:40].sum())
#     data = X_fit.transform(data)

# print(X_train.shape)
# print(X_predict.shape)
# sleep(100)

# play_style_df = pd.DataFrame({'id':all_stats_df['id'], 'player_id':all_stats_df['player_id'], 'player_name':all_stats_df['player_name'], 'season_end':all_stats_df['season_end']})

#X_details = X_wins[['player_name', 'season_end']].reset_index(drop=True)
# X_wins= X_transformed
y_train = full_data_df.iloc[:, 5]
y_train = np.ravel(y_train)

'''
X_train = pd.DataFrame(X_train)
X_train['player_name'] = full_data_df.loc[:, 'player_name']
X_train['season_end'] = full_data_df.loc[:, 'season_end']
'''
# X_losses= 0
# y_losses = 0

# y_losses = np.ravel(y_losses)

# grid_search(X_transformed, y_wins)
'''
X_train, X_test_wins, y_train, y_test_wins = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
X_train = X_train.drop(columns=['player_name', 'season_end'])
X_test_details = X_test_wins[['player_name', 'season_end']].reset_index(drop=True)
X_test_wins = X_test_wins.drop(columns=['player_name', 'season_end'])
'''

# # X_train_losses, X_test_losses, y_train_losses, y_test_losses = train_test_split(X_losses, y_losses, test_size=0.25, random_state=42)
# y_test_wins = np.ravel(y_test_wins)
# y_train_wins = np.ravel(y_train_wins)


params = {'min_samples_leaf': 12, 'max_depth':10, 'subsample':.5, 'n_estimators':5000, 'min_samples_split':14, 'loss': 'ls', 'learning_rate': .01}
wins_model = ensemble.GradientBoostingRegressor(**params)
#losses_model = ensemble.GradientBoostingRegressor(**params)

print('training model')
#wc_model = wins_model.fit(X_train_wins, y_train_wins)
wc_model = wins_model.fit(X_train, y_train)
#losses_model.fit(X_train_losses, y_train_losses)

print('predicting')
predicted_2020_wc = wc_model.predict(X_predict)

predict_2020_wc_df = pd.DataFrame()
predict_2020_wc_df['player_name'] = X_predict_details
predict_2020_wc_df['wins_contr'] = predicted_2020_wc
print(predict_2020_wc_df.sort_values('wins_contr'))

'''
wins_mse = mean_squared_error(y_test_wins, wins_model.predict(X_test_wins))
wins_rmse = np.sqrt(wins_mse)

predicted_v_actual = pd.DataFrame()
predicted_v_actual['actual'] = y_test_wins
predicted_v_actual['predicted'] = wins_model.predict(X_test_wins)
predicted_v_actual['difference'] = abs(predicted_v_actual['actual'] -predicted_v_actual['predicted'])
predicted_v_actual = X_test_details.join(predicted_v_actual)
print(predicted_v_actual.sort_values('predicted', ascending=False)[0:50])


print(wins_rmse)
'''

# losses_mse = mean_squared_error(y_test_losses, losses_model.predict(X_test_losses))
# losses_rmse = np.sqrt(losses_mse)

# team_ids = [1610612737, 1610612738, 1610612751, 1610612766, 1610612741, 1610612739, 1610612742, 
#             1610612743, 1610612765, 1610612744, 1610612745, 1610612754, 1610612746, 1610612747, 
#             1610612763, 1610612748, 1610612749, 1610612750, 1610612740, 1610612752, 1610612760, 
#             1610612753, 1610612755, 1610612756, 1610612757, 1610612758, 1610612759, 1610612761, 
#             1610612762, 1610612764]

# league_df = pd.DataFrame()
# for team_id in team_ids:
#     team_info = teams.find_team_name_by_id(team_id)
#     team_name = team_info.get('full_name')
#     print(team_name + '' +str(team_id))
#     team_roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=2019).common_team_roster.get_data_frame()
#     team_df = team_roster[['PLAYER_ID', 'TeamID', 'SEASON', 'PLAYER', 'AGE', 'EXP']]
#     team_df = team_df.rename(columns={'PLAYER_ID':'player_id', 'TeamID':'team_id', 'SEASON':'season_end', 'PLAYER':'player_name', 'AGE':'age', 'EXP':'exp'})
#     team_df['team_name'] = team_name
#     league_df = league_df.append(team_df)
