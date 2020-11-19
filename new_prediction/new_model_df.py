import pandas as pd 
import numpy as np
import psycopg2 as pg2
import sys
sys.path.append("..")
from similarity_analysis.player_groups import group_players
from similarity_analysis.clustering_functions import standardize
from time import sleep
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from player_prediction import grid_search
from nba_api.stats.endpoints import drafthistory


def initial_player_prediction_df(team_similarity_df, player_similarity_df, seasons_list, injured_players_list, grouped_teams, grouped_players):

    seasons = seasons_list

    draft_df = pd.DataFrame()
    for season in seasons:
        draft = drafthistory.DraftHistory(season_year_nullable=season)
        draft_df = draft_df.append(draft.draft_history.get_data_frame())

    draft_df = draft_df[['PLAYER_NAME', 'OVERALL_PICK']]
    draft_df = draft_df.rename(columns={'PLAYER_NAME':'player_name', 'OVERALL_PICK':'overall_pick'})

    # print(len(grouped_teams))
    # print(len(grouped_players))

    teams_group_reversed = {}
    players_group_reversed = {}

    for group in grouped_teams:
        for team in grouped_teams[group]:
            teams_group_reversed[team] = group

    for group in grouped_players:
        for player in grouped_players[group]:
            players_group_reversed[player] = group

    # print(len(teams_group_reversed))
    # print(len(players_group_reversed))

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    wins_contr_query = """SELECT player_id, season_end, player_name, SUM(value_contributed) wins_contr, AVG(value_contributed) avg_wins
                            FROM all_seasons_value_contributed
                            WHERE season_type = 'Regular Season'
                            AND win_loss = 1
                            GROUP BY player_id, player_name, season_end;"""

    losses_contr_query = """SELECT player_id, season_end, player_name, SUM(value_contributed) losses_contr, AVG(value_contributed) avg_losses
                            FROM all_seasons_value_contributed
                            WHERE season_type = 'Regular Season'
                            AND win_loss = 0
                            GROUP BY player_id, player_name, season_end;"""

    model_query = """SELECT COUNT(game_id) games_played, player_id, team_id, player_name, season_end 
                        FROM all_seasons_value_contributed
                        WHERE season_type = 'Regular Season'
                        GROUP BY player_id, player_name, team_id, season_end;"""

    age_exp_query = """SELECT *
                        FROM age_exp;"""

    prediction_query = """SELECT *
                            FROM league_rosters
                            WHERE season_end = '2019';"""

    wins_contr_df = pd.read_sql(wins_contr_query, con=conn)
    losses_contr_df = pd.read_sql(losses_contr_query, con=conn)
    age_exp_df = pd.read_sql(age_exp_query, con=conn)
    model_df = pd.read_sql(model_query, con=conn)
    prediction_df = pd.read_sql(prediction_query, con=conn)

    conn.close()

    injured_players = injured_players_list

    for player in injured_players:
        prediction_df = prediction_df[prediction_df['player_name'] != player]

    prediction_df = prediction_df.reset_index(drop=True)

    prediction_df['season_end'] = 2020
    prediction_df = prediction_df[['player_id', 'team_id', 'player_name', 'season_end',]]
    prediction_df['player_season_id'] = [str(prediction_df.loc[x, 'player_id']) + '_' + str(prediction_df.loc[x, 'season_end']) for x in range(len(prediction_df))]
    prediction_df['team_season_id'] = [str(prediction_df.loc[x, 'team_id']) + '_' + str(prediction_df.loc[x, 'season_end']) for x in range(len(prediction_df))]
    prediction_df['player_id'] = prediction_df['player_id'].astype(int)
    # prediction_df['team_id'] = prediction_df['player_id'].astype(int)

    model_df['player_season_id'] = [str(model_df.loc[x, 'player_id']) + '_' + str(model_df.loc[x, 'season_end']) for x in range(len(model_df))]
    model_df['team_season_id'] = [str(model_df.loc[x, 'team_id']) + '_' + str(model_df.loc[x, 'season_end']) for x in range(len(model_df))]
    wins_contr_df['player_season_id'] = [str(wins_contr_df.loc[x, 'player_id']) + '_' + str(wins_contr_df.loc[x, 'season_end']) for x in range(len(wins_contr_df))]
    losses_contr_df['player_season_id'] = [str(losses_contr_df.loc[x, 'player_id']) + '_' + str(losses_contr_df.loc[x, 'season_end']) for x in range(len(losses_contr_df))]

    model_df = model_df.sort_values('games_played', ascending=False).drop_duplicates(subset='player_season_id')
    model_df = model_df[model_df['season_end'] >= 2015].reset_index(drop=True)
    model_df = model_df.drop(columns='games_played')
    # print(len(model_df))

    age_exp_df = age_exp_df[['player_id', 'season_end','age', 'exp']]
    age_exp_df['player_season_id'] = [str(age_exp_df.loc[x, 'player_id']) + '_' + str(age_exp_df.loc[x, 'season_end']) for x in range(len(age_exp_df))]
    age_exp_df = age_exp_df[['player_season_id', 'age', 'exp']]
    model_df = model_df.merge(age_exp_df, on='player_season_id')

    age_list = []
    exp_list = []
    for idx in range(len(prediction_df)):
        player_id = prediction_df.loc[idx, 'player_id']
        previous_season = int(prediction_df.loc[idx, 'season_end']) - 1
        previous_unique = str(player_id) + '_' + str(previous_season)
        try:
            age_list.append(float(age_exp_df[age_exp_df['player_season_id'] == previous_unique].reset_index(drop=True).loc[0, 'age']))
            exp_list.append(float(age_exp_df[age_exp_df['player_season_id'] == previous_unique].reset_index(drop=True).loc[0, 'exp']))
        except:
            age_list.append(0)
            exp_list.append(0)

    prediction_df['age'] = age_list
    prediction_df['exp'] = exp_list

    model_df = model_df.append(prediction_df).reset_index(drop=True)
    # print(model_df)
    wins_contr_list = []
    losses_contr_list = []
    avg_wins_contr_list = []
    avg_losses_contr_list = []
    previous_season_player_groups = []
    season_team_groups = []
    recent_wins_list = []
    recent_losses_list = []
    max_wins_list = []
    max_losses_list = []
    for idx, player_id in model_df['player_id'].iteritems():
        # print(str(idx) + ' / ' + str(len(model_df)))
        previous_season = int(model_df.loc[idx, 'season_end']) - 1
        previous_season_player_id = str(player_id) + '_' + str(previous_season)
        season_team_id = str(model_df.loc[idx, 'team_id']) + '_' + str(model_df.loc[idx, 'season_end'])
        wins_median_list = []
        avg_wins_median_list = []
        losses_median_list = []
        avg_losses_median_list = []
        no_season_counter = 0
        for year in range(6):
            try:
                wins_median_list.append(wins_contr_df[(wins_contr_df['player_id'] == player_id) & (wins_contr_df['season_end'] == model_df.loc[idx, 'season_end'] - year - 1)].reset_index(drop=True).loc[0, 'wins_contr'])
                avg_wins_median_list.append(wins_contr_df[(wins_contr_df['player_id'] == player_id) & (wins_contr_df['season_end'] == model_df.loc[idx, 'season_end'] - year - 1)].reset_index(drop=True).loc[0, 'avg_wins'])
                losses_median_list.append(losses_contr_df[(losses_contr_df['player_id'] == player_id) & (losses_contr_df['season_end'] == model_df.loc[idx, 'season_end'] - year - 1)].reset_index(drop=True).loc[0, 'losses_contr'])
                avg_losses_median_list.append(losses_contr_df[(losses_contr_df['player_id'] == player_id) & (losses_contr_df['season_end'] == model_df.loc[idx, 'season_end'] - year - 1)].reset_index(drop=True).loc[0, 'avg_losses'])
            except:
                no_season_counter += 1
                wins_median_list.append(0)
                losses_median_list.append(0)
                avg_wins_median_list.append(0)
                avg_losses_median_list.append(0)
            if no_season_counter == 4 or no_season_counter == 5:
                list_item = 5
            elif no_season_counter == 3 or no_season_counter == 2:
                list_item = 4
            else:
                list_item = 3
        median_wins = sorted(wins_median_list)[list_item]
        median_losses = sorted(losses_median_list)[list_item]
        avg_median_wins = sorted(avg_wins_median_list)[list_item]
        avg_median_losses = sorted(avg_losses_median_list)[list_item]

        wins_contr_list.append(median_wins)
        losses_contr_list.append(median_losses)
        avg_wins_contr_list.append(avg_median_wins)
        avg_losses_contr_list.append(avg_median_losses)
        max_wins_list.append(sorted(wins_median_list)[5])
        max_losses_list.append(sorted(wins_median_list)[5])
        
        try:
            recent_wins_list.append(wins_contr_df[(wins_contr_df['player_id'] == player_id) & (wins_contr_df['season_end'] == previous_season)].reset_index(drop=True).loc[0, 'wins_contr'])
        except:
            recent_wins_list.append(0)
        try:
            recent_losses_list.append(losses_contr_df[(losses_contr_df['player_id'] == player_id) & (losses_contr_df['season_end'] == previous_season)].reset_index(drop=True).loc[0, 'losses_contr'])
        except:
            recent_losses_list.append(0)

        try:
            previous_season_player_groups.append(players_group_reversed[previous_season_player_id])
        except:
            previous_season_player_groups.append(213)
        season_team_groups.append(teams_group_reversed[season_team_id])

    model_df['median_wins'] = wins_contr_list
    model_df['median_losses'] = losses_contr_list
    # print(len(recent_wins_list))
    model_df['previous_wins'] = recent_wins_list
    model_df['previous_losses'] = recent_losses_list
    model_df['max_wins'] = max_wins_list
    model_df['max_losses'] = max_losses_list
    model_df['med_avg_per_win'] = avg_wins_contr_list
    model_df['med_avg_per_loss'] = avg_losses_contr_list
    model_df['player_style_group'] = previous_season_player_groups
    model_df['team_comp_group'] = season_team_groups
    # print(model_df)
    model_df = model_df.merge(draft_df, on='player_name', how="outer")
    model_df = model_df.fillna(0)

    standardized = standardize(model_df.iloc[:, 6:17].to_numpy())
    # print(standardized)

    standardized_columns = ['age', 'exp', 'median_wins', 'median_losses', 'previous_wins', 'previous_losses', 'max_wins', 'max_losses', 'med_avg_per_win', 'med_avg_per_loss', 'overall_pick']
    for idx, column in enumerate(standardized_columns):
        model_df[column] = standardized[:,idx]


    # print(model_df)
    player_style_dummies = pd.get_dummies(model_df['player_style_group'], prefix='player_style_group')
    team_comp_dummies = pd.get_dummies(model_df['team_comp_group'], prefix='team_comp_group')
    # team_id_dummies = pd.get_dummies(model_df['team_id'], prefix='team_id')
    model_df = model_df.drop(columns=['player_style_group', 'team_comp_group'])
    model_df = model_df.join(player_style_dummies)
    # print(model_df)
    model_df = model_df.join(team_comp_dummies)
    # print(model_df)
    # model_df = model_df.join(team_id_dummies)
    initial_prediction_df = model_df.reset_index(drop=True)
    # print(prediction_df)
    fit_model_df = model_df[model_df['season_end'] != 2020].reset_index(drop=True)

    fit_model_df = fit_model_df.merge(wins_contr_df[['player_season_id', 'wins_contr']], on='player_season_id').reset_index(drop=True)
    fit_model_df = fit_model_df.merge(losses_contr_df[['player_season_id', 'losses_contr']], on='player_season_id').reset_index(drop=True)
    # print(model_df)


    y_wins = fit_model_df['wins_contr']
    y_losses = fit_model_df['losses_contr']

    y_initial_wins = np.ravel(y_wins)
    y_initial_losses = np.ravel(y_losses)

    X_initial_model = fit_model_df.iloc[:, 6:-2]
    initial_model_details_df = fit_model_df.iloc[:, 2:6]

    
    X_initial_predict = initial_prediction_df.iloc[:, 6:]
    initial_predict_details_df = initial_prediction_df.iloc[:, 2:6]


    final_model_df = initial_prediction_df.iloc[:, 2:]
    # print('first final model')
    # print(final_model_df.tail(100))

    return final_model_df, X_initial_predict, initial_predict_details_df, X_initial_model, initial_model_details_df, y_initial_wins, y_initial_losses

# print('starting grid search')
# grid_search(model_df.iloc[:, 5:-2], y_wins)
# grid_search(model_df.iloc[:, 5:-2], y_losses)

# X_train, X_test_wins, y_train, y_test_wins = train_test_split(model_df, y_wins, test_size=0.2, random_state=42)
# X_train = X_train.iloc[:, 5:-2]
# X_test_details = X_test_wins[['player_name', 'season_end']].reset_index(drop=True)
# X_test_wins = X_test_wins.iloc[:, 5:-2]

# X_train, X_test_losses, y_train, y_test_losses = train_test_split(model_df, y_losses, test_size=0.2, random_state=42)
# X_train = X_train.iloc[:, 5:-2]
# X_test_details = X_test_losses[['player_name', 'season_end']].reset_index(drop=True)
# X_test_losses = X_test_losses.iloc[:, 5:-2]


def create_team_record_df(start_season, end_season, initial_wc_model_fit, initial_lc_model_fit, X_initial_model, initial_model_details_df, X_initial_predict, initial_predict_details_df, final_model_df):

    #predict_season = seasons_list

    X_initial_model = X_initial_model.merge(initial_model_details_df, how='outer', left_index=True, right_index=True)
    team_model_details = X_initial_model[(X_initial_model['season_end'] >= start_season) & (X_initial_model['season_end'] <= end_season)].iloc[:, -len(initial_model_details_df.columns):]
    X_initial_model = X_initial_model[(X_initial_model['season_end'] >= start_season) & (X_initial_model['season_end'] <= end_season)].iloc[:, :-len(initial_model_details_df.columns)]
    

    # for idx, season in enumerate(predict_season):
    #     print('predicting first model: ' + str(season))
    #     if idx + 1 != len(seasons_list):
    #         first_team_modelion_df = model_df[model_df['season_end'] == season].reset_index(drop=True)
    #         prediction_season_details = first_team_modelion_df.iloc[:, 2:4]
    #         first_team_modelion_df = first_team_modelion_df.iloc[:, 5:-2]
            

    #     else:
    #         prediction_season_details = prediction_df.iloc[:, 2:4]
    #         first_team_modelion_df = prediction_df.iloc[:, 5:]

    team_model_df = pd.DataFrame()
    team_model_df['player_name'] = team_model_details['player_name']
    team_model_df['team_season_id'] = team_model_details['team_season_id']
    team_model_df['predicted_wc'] = initial_wc_model_fit.predict(X_initial_model)
    team_model_df['predicted_lc'] = initial_lc_model_fit.predict(X_initial_model)
    team_model_df['predicted_vc'] = team_model_df['predicted_wc'] + team_model_df['predicted_lc']

    team_predict_df = pd.DataFrame()
    team_predict_df['player_name'] = initial_predict_details_df['player_name']
    team_predict_df['team_season_id'] = initial_predict_details_df['team_season_id']
    team_predict_df['predicted_wc'] = initial_wc_model_fit.predict(X_initial_predict)
    team_predict_df['predicted_lc'] = initial_lc_model_fit.predict(X_initial_predict)
    team_predict_df['predicted_vc'] = team_predict_df['predicted_wc'] + team_predict_df['predicted_lc']

    final_model_df['predicted_wc'] = initial_wc_model_fit.predict(X_initial_predict)
    final_model_df['predicted_lc'] = initial_lc_model_fit.predict(X_initial_predict)
    final_model_df['predicted_vc'] = team_predict_df['predicted_wc'] + team_predict_df['predicted_lc']

        # predict_season_df = pd.DataFrame()
        # predict_season_df['player_name'] = prediction_season_details['player_name']
        # predict_season_df['team_id'] = prediction_season_details['team_id']
        # predict_season_df['wins_contr'] = predicted_season_wc
        # predict_season_df['losses_contr'] = predicted_season_lc

        # print(predict_season_df.sort_values('wins_contr', ascending=False))

        # if season != 2020:
        #     prediction_df2 = model_df[model_df['season_end'] == season].reset_index(drop=True).drop(columns=['wins_contr', 'losses_contr'])
        #     y_df2 = model_df[model_df['season_end'] == season].reset_index(drop=True)[['wins_contr', 'losses_contr']]
        # else:
        #     prediction_df2 = prediction_df
        # prediction_df2['predicted_wc'] = predict_season_df['wins_contr']
        # prediction_df2['predicted_lc'] = predict_season_df['losses_contr']
        # prediction_df2['predicted_vc'] = predict_season_df['losses_contr'] + predict_season_df['wins_contr']

        # final_prediction_df = final_prediction_df.append(prediction_df2)
        # print(final_prediction_df)
        # if season != 2020:
        #     final_y = final_y.append(y_df2)
        # else:
        #     pass

    X_team_model = pd.DataFrame(columns=['team_season_id', 'top_3_w', 'top_3_l', 'top_6_w', 'top_6_l', 'top_9_w', 'top_9_l'])
    for team in team_model_df['team_season_id'].unique():
        current_team = team_model_df[team_model_df['team_season_id'] == team].sort_values('predicted_vc', ascending=False).reset_index(drop=True)
        # print(current_team)
        projected_top_3_wins = current_team.loc[0:3, 'predicted_wc'].sum()
        projected_top_3_losses = current_team.loc[0:3, 'predicted_lc'].sum() 
        projected_top_6_wins = current_team.loc[0:6, 'predicted_wc'].sum()
        projected_top_6_losses = current_team.loc[0:6, 'predicted_lc'].sum() 
        projected_top_9_wins = current_team.loc[0:9, 'predicted_wc'].sum()
        projected_top_9_losses = current_team.loc[0:9, 'predicted_lc'].sum() 

        X_team_model.loc[len(X_team_model)] = [team, projected_top_3_wins, projected_top_3_losses, projected_top_6_wins, projected_top_6_losses, projected_top_9_wins, projected_top_9_losses]

    X_team_predict = pd.DataFrame(columns=['team_season_id', 'top_3_w', 'top_3_l', 'top_6_w', 'top_6_l', 'top_9_w', 'top_9_l'])
    for team in team_predict_df['team_season_id'].unique():
        current_team = team_predict_df[team_predict_df['team_season_id'] == team].sort_values('predicted_vc', ascending=False).reset_index(drop=True)
        # print(current_team)
        projected_top_3_wins = current_team.loc[0:3, 'predicted_wc'].sum()
        projected_top_3_losses = current_team.loc[0:3, 'predicted_lc'].sum() 
        projected_top_6_wins = current_team.loc[0:6, 'predicted_wc'].sum()
        projected_top_6_losses = current_team.loc[0:6, 'predicted_lc'].sum() 
        projected_top_9_wins = current_team.loc[0:9, 'predicted_wc'].sum()
        projected_top_9_losses = current_team.loc[0:9, 'predicted_lc'].sum() 

        X_team_predict.loc[len(X_team_predict)] = [team, projected_top_3_wins, projected_top_3_losses, projected_top_6_wins, projected_top_6_losses, projected_top_9_wins, projected_top_9_losses]

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    team_wins_query = """SELECT team_id, season_end, SUM(value_contributed) actual_wins
                            FROM all_seasons_value_contributed
                            WHERE season_type = 'Regular Season'
                            AND win_loss = 1
                            GROUP BY team_id, season_end;"""

    team_losses_query = """SELECT team_id, season_end, SUM(value_contributed) actual_losses
                            FROM all_seasons_value_contributed
                            WHERE season_type = 'Regular Season'
                            AND win_loss = 0
                            GROUP BY team_id, season_end;"""

    team_wins_df = pd.read_sql(team_wins_query, con=conn)
    team_losses_df = pd.read_sql(team_losses_query, con=conn)

    conn.close()

    team_wins_df['team_season_id'] = [str(team_wins_df.loc[x, 'team_id']) + '_' + str(team_wins_df.loc[x, 'season_end']) for x in range(len(team_wins_df))]
    team_losses_df['team_season_id'] = [str(team_losses_df.loc[x, 'team_id']) + '_' + str(team_losses_df.loc[x, 'season_end']) for x in range(len(team_losses_df))]
    team_wins_df = team_wins_df[['team_season_id', 'actual_wins']]
    team_losses_df = team_losses_df[['team_season_id', 'actual_losses']]

    X_team_model = X_team_model.merge(team_wins_df, on='team_season_id')
    X_team_model = X_team_model.merge(team_losses_df, on='team_season_id')
    

    X_team_model_standardized = standardize(X_team_model.iloc[:, 1:-2].to_numpy())
    for idx, column in enumerate(X_team_model.columns[1:-2]):
        X_team_model[column] = X_team_model_standardized[:, idx]
    


    X_team_predict_standardized = standardize(X_team_predict.iloc[:, 1:].to_numpy())
    for idx, column in enumerate(X_team_predict.columns[1:]):
        X_team_predict[column] = X_team_predict_standardized[:, idx]

    y_team_wins = X_team_model['actual_wins']
    y_team_losses = X_team_model['actual_losses']
    team_model_detail = X_team_model['team_season_id']
    X_team_model = X_team_model.iloc[:, 1:-2]
    
    team_predict_detail = X_team_predict.iloc[:, 0]
    X_team_predict = X_team_predict.iloc[:, 1:]
    

    return final_model_df, X_team_predict, team_predict_detail, X_team_model, team_model_detail, y_team_wins, y_team_losses



# print('training second model')
# min_samples_leaf = 7
# max_depth = 7
# subsample = .48
# n_estimators = 1000
# min_samples_split = 6
# print('leaf: ' + str(min_samples_leaf))
# print('depth: ' + str(max_depth))
# print('sub: ' + str(subsample))
# print('n_estimators: ' + str(n_estimators))
# print('split: ' + str(min_samples_split))
# team_wins_params = {'min_samples_leaf': min_samples_leaf, 'max_depth':max_depth, 'subsample':subsample, 'n_estimators':n_estimators, 'min_samples_split':min_samples_split, 'loss': 'ls', 'learning_rate': .01}
# team_losses_params = {'min_samples_leaf': min_samples_leaf, 'max_depth':max_depth, 'subsample':subsample, 'n_estimators':n_estimators, 'min_samples_split':min_samples_split, 'loss': 'ls', 'learning_rate': .01}
# team_wins_model = ensemble.GradientBoostingRegressor(**team_wins_params)
# team_losses_model = ensemble.GradientBoostingRegressor(**team_losses_params)

# team_wins_model = team_wins_model.fit(model_team_df.iloc[:, 1:-2], team_wins)
# team_losses_model = team_losses_model.fit(model_team_df.iloc[:, 1:-2], team_losses)


# predicted_team_record = pd.DataFrame()
# predicted_season_wins = team_wins_model.predict(projected_team_df.iloc[:, 1:])
# predicted_season_losses = team_losses_model.predict(projected_team_df.iloc[:, 1:])
# predicted_team_record['team_season_id'] = projected_team_df.iloc[:, 0]
# predicted_team_record['predicted_team_wins'] = predicted_season_wins
# predicted_team_record['predicted_team_losses'] = predicted_season_losses
# print(predicted_team_record)

# print('DF2_LEN: ' + str(len(final_prediction_df)))
# final_prediction_df = final_prediction_df.reset_index(drop=True)
# print(final_prediction_df)
# final_prediction_df['team_season_id'] = [str(final_prediction_df.loc[x, 'team_id']) + '_' + str(final_prediction_df.loc[x, 'season_end'])[:-2] for x in range(len(final_prediction_df))]
# print(final_prediction_df)
# final_prediction_df = pd.merge(final_prediction_df, predicted_team_record, how='left')
# print('DF2_LEN: ' + str(len(final_prediction_df)))
# print(final_prediction_df)

# final_model_df = final_prediction_df[final_prediction_df['season_end'] != 2020]
# final_model_df = final_model_df.drop(columns='team_season_id')

# predict_2020_df = final_prediction_df[final_prediction_df['season_end'] == 2020]
# predict_2020_df = predict_2020_df.drop(columns='team_season_id')
# print(final_model_df)

# print(predict_2020_df)

# final_y_wins = final_y['wins_contr']
# final_y_losses = final_y['losses_contr']




# print('training last model')
# min_samples_leaf = 7
# max_depth = 7
# subsample = .48
# n_estimators = 1000
# min_samples_split = 6
# print('leaf: ' + str(min_samples_leaf))
# print('depth: ' + str(max_depth))
# print('sub: ' + str(subsample))
# print('n_estimators: ' + str(n_estimators))
# print('split: ' + str(min_samples_split))
# wc_params = {'min_samples_leaf': min_samples_leaf, 'max_depth':max_depth, 'subsample':subsample, 'n_estimators':n_estimators, 'min_samples_split':min_samples_split, 'loss': 'ls', 'learning_rate': .01}
# min_samples_leaf = 6
# min_samples_split = 4

# lc_params = {'min_samples_leaf': min_samples_leaf, 'max_depth':max_depth, 'subsample':subsample, 'n_estimators':n_estimators, 'min_samples_split':min_samples_split, 'loss': 'ls', 'learning_rate': .01}
# wc_model = ensemble.GradientBoostingRegressor(**wc_params)
# lc_model = ensemble.GradientBoostingRegressor(**lc_params)

# wc_model = wc_model.fit(final_model_df.iloc[:, 5:], final_y_wins)
# lc_model = lc_model.fit(final_model_df.iloc[:, 5:], final_y_losses)


# #2020 PREDICTION CODE

# predicted_2020_wc = wc_model.predict(predict_2020_df.iloc[:, 5:])
# predicted_2020_lc = lc_model.predict(predict_2020_df.iloc[:, 5:])
# prediction_2020_details = predict_2020_df.iloc[:, 2:4]

# predicted_2020_df = pd.DataFrame()
# predicted_2020_df['player_name'] = prediction_2020_details['player_name']
# predicted_2020_df['team_id'] = prediction_2020_details['team_id']
# predicted_2020_df['wins_contr'] = predicted_2020_wc
# predicted_2020_df['losses_contr'] = predicted_2020_lc
# predicted_2020_df['value_contr'] = predicted_2020_df['wins_contr'] + predicted_2020_df['losses_contr']
# predicted_2020_df['difference'] = predicted_2020_df['wins_contr'] - predicted_2020_df['losses_contr']
# print(predicted_2020_df.sort_values('wins_contr', ascending=False).reset_index(drop=True)[0:50])
# print(predicted_2020_df.sort_values('losses_contr', ascending=False)[0:50])
# print(predicted_2020_df.sort_values('difference', ascending=False)[0:50])

# for team in predicted_2020_df['team_id'].unique():
#         current_team = predicted_2020_df[predicted_2020_df['team_id'] == team].sort_values('value_contr', ascending=False).reset_index(drop=True)
#         print(current_team)
#         print('Projected Wins: ' + str(current_team.loc[0:8,'wins_contr'].sum()))
#         print('Projected Losses: ' + str(current_team.loc[0:8,'losses_contr'].sum()))



# wc_model = wins_model.fit(X_train, y_train)
# #losses_model.fit(X_train_losses, y_train_losses)


# wins_mse = mean_squared_error(y_test_wins, wins_model.predict(X_test_wins))
# wins_rmse = np.sqrt(wins_mse)

# predicted_v_actual = pd.DataFrame()
# predicted_v_actual['actual'] = y_test_wins
# predicted_v_actual['predicted'] = wins_model.predict(X_test_wins)
# predicted_v_actual['difference'] = abs(predicted_v_actual['actual'] -predicted_v_actual['predicted'])
# predicted_v_actual = X_test_details.join(predicted_v_actual)
# print(predicted_v_actual.sort_values('actual', ascending=False)[0:50])
# print(predicted_v_actual.sort_values('predicted', ascending=False)[0:50])


# print(wins_rmse)

    





