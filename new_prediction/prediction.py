import sys
sys.path.append("..")
import math
import pandas as pd
from new_model_df import initial_player_prediction_df, create_team_record_df
from sklearn import ensemble
from player_prediction import grid_search
import psycopg2 as pg2
from similarity_analysis.clustering_functions import standardize
from similarity_analysis.player_groups import group_players

team_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_injured_excluded_aligned.csv')
player_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_5.csv')

initial_seasons_list = [2013,2014,2015,2016,2017,2018,2019]
injured_players_list = ['Kevin Durant', 'DeMarcus Cousins', 'John Wall', 'Andre Iguodala', 'Darius Miller', 'Paul George', 'Victor Oladipo', 'Jusuf Nurkic', 'Klay Thompson', 'Gerald Green']

team_projection_df = pd.DataFrame()
player_projection_df = pd.DataFrame()

def predict_season(team_similarity_df, player_similarity_df, initial_seasons_list, injured_players_list, runs, team_projection_df, player_projection_df, n_estimators, injuries, grouped_teams, grouped_players):
    final_model_df, X_initial_predict, initial_predict_details_df, X_initial_model, initial_model_details_df, y_initial_wins, y_initial_losses = initial_player_prediction_df(team_similarity_df, player_similarity_df, initial_seasons_list, injured_players_list, grouped_teams, grouped_players)

    for run in range(runs):
        print(str(run) + ' / ' + str(runs))
        ### Fit Initial Model Start ###
        initial_wc_params = {'min_samples_leaf': 33, 'max_depth':25, 
                        'subsample':.2, 'n_estimators':n_estimators, 
                        'min_samples_split':15, 'loss': 'ls', 'learning_rate': .01}

        initial_lc_params = {'min_samples_leaf': 40, 'max_depth':15, 
                        'subsample':.2, 'n_estimators':n_estimators, 
                        'min_samples_split':9, 'loss': 'ls', 'learning_rate': .01}

        #-3.5705 1000, depth:25, leaf:33, split:15, sub:.2
        #-3.5721 1000, depth:26, leaf:33, split:14, sub:.21
        # wc_test_params = {'min_samples_leaf':[33,32,34], 'max_depth':[26, 27, 25], 'min_samples_split':[14, 15, 13], 'subsample':[.22,.2,.21]}
        #-3.5507 1000, depth:15, leaf:40, split:9, sub:.2
        # lc_test_params = {'min_samples_leaf':[38,37,39], 'max_depth':[17, 16, 15], 'min_samples_split':[7, 9, 8], 'subsample':[.21,.2,.19]}

        # print('grid_search_start')
        # grid_search(X_initial_model, y_initial_wins, initial_wc_params, wc_test_params)
        # grid_search(X_initial_model, y_initial_losses, initial_lc_params, lc_test_params)

        initial_wc_model = ensemble.GradientBoostingRegressor(**initial_wc_params)
        initial_lc_model = ensemble.GradientBoostingRegressor(**initial_lc_params)




        initial_wc_model_fit = initial_wc_model.fit(X_initial_model, y_initial_wins)
        initial_lc_model_fit = initial_lc_model.fit(X_initial_model, y_initial_losses)
        ### Fit Initital Model End ###

        final_model_df, X_team_predict, team_predict_detail, X_team_model, team_model_detail, y_team_wins, y_team_losses = create_team_record_df(2015, 2019, initial_wc_model_fit, initial_lc_model_fit, X_initial_model, initial_model_details_df, X_initial_predict, initial_predict_details_df, final_model_df,)


        ### Fit Team Records Model Start ###
        team_wins_params = {'min_samples_leaf': 2, 'max_depth':8, 
                                'subsample':.2, 'n_estimators':n_estimators, 
                                'min_samples_split':23, 'loss': 'ls', 'learning_rate': .01}

        team_losses_params = {'min_samples_leaf': 2, 'max_depth':6, 
                                    'subsample':.16, 'n_estimators':n_estimators, 
                                    'min_samples_split':15, 'loss': 'ls', 'learning_rate': .01}

        team_wins_model = ensemble.GradientBoostingRegressor(**team_wins_params)
        team_losses_model = ensemble.GradientBoostingRegressor(**team_losses_params)

        #-.00525 1000, depth:8, leaf:2, split:23, sub:.2
        wc_test_params = {'min_samples_leaf':[3,5,7,9], 'max_depth':[9,11,13,15], 'min_samples_split':[24,20,22,18], 'subsample':[.19,.17,.21,.13]}
        #-.00506 1000, depth:6, leaf:2, split:15, sub:.15
        lc_test_params = {'min_samples_leaf':[3,4,5], 'max_depth':[8,6,5,10], 'min_samples_split':[14,15,16,17,18], 'subsample':[.12,.14,.15,.16]}

        # print('grid_search_start')
        # grid_search(X_team_model, y_team_wins, team_wins_params, wc_test_params)
        # grid_search(X_team_model, y_team_losses, team_losses_params, lc_test_params)

        team_wins_model_fit = team_wins_model.fit(X_team_model, y_team_wins)
        team_losses_model_fit = team_losses_model.fit(X_team_model, y_team_losses)
        ### Fit Team Records Model End ###


        ### Predict Team Records Start ###
        predicted_team_wins = team_wins_model_fit.predict(X_team_predict)
        predicted_team_losses = team_losses_model_fit.predict(X_team_predict)

        team_record_predictions = pd.DataFrame()
        team_record_predictions['team_season_id'] = team_predict_detail
        team_record_predictions['predicted_team_wins'] = predicted_team_wins
        team_record_predictions['predicted_team_losses'] = predicted_team_losses

        ### Predict Team Record End ###

        ### Create Final Prediction Model and Predict DataFrames Start ###
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

        wins_contr_df = pd.read_sql(wins_contr_query, con=conn)
        losses_contr_df = pd.read_sql(losses_contr_query, con=conn)
        conn.close()

        wins_contr_df['player_season_id'] = [str(wins_contr_df.loc[x, 'player_id']) + '_' + str(wins_contr_df.loc[x, 'season_end']) for x in range(len(wins_contr_df))]
        losses_contr_df['player_season_id'] = [str(losses_contr_df.loc[x, 'player_id']) + '_' + str(losses_contr_df.loc[x, 'season_end']) for x in range(len(losses_contr_df))]


        final_model_df = pd.merge(final_model_df, team_record_predictions, how='left')
        X_final_model = final_model_df[final_model_df['season_end'] != 2020]
        X_final_model = X_final_model.merge(wins_contr_df[['player_season_id', 'wins_contr']], on='player_season_id').reset_index(drop=True)
        X_final_model = X_final_model.merge(losses_contr_df[['player_season_id', 'losses_contr']], on='player_season_id').reset_index(drop=True)


        y_final_wins = X_final_model.iloc[:, -2]
        y_final_losses = X_final_model.iloc[:, -1]
        X_final_model = X_final_model.iloc[:, 4:-2]


        X_final_predict = final_model_df[final_model_df['season_end'] == 2020]
        final_prediction_details = X_final_predict.iloc[:, :4]
        X_final_predict = X_final_predict.iloc[:, 4:]
        ### Create Final Prediction Model and Predict DataFrames End###


        ### Fit Final Predict Model Start ###
        final_wc_params = {'min_samples_leaf': 2, 'max_depth':3, 
                                'subsample':.57, 'n_estimators':n_estimators, 
                                'min_samples_split':13, 'loss': 'ls', 'learning_rate': .01}

        final_lc_params = {'min_samples_leaf': 13, 'max_depth':4, 
                                    'subsample':.33, 'n_estimators':n_estimators, 
                                    'min_samples_split':8, 'loss': 'ls', 'learning_rate': .01}

        final_wc_model = ensemble.GradientBoostingRegressor(**final_wc_params)
        final_lc_model = ensemble.GradientBoostingRegressor(**final_lc_params)

        #-1.342613 1000, depth:3, leaf:2, split:13, sub:.57
        wc_test_params = {'min_samples_leaf':[2,3,4], 'max_depth':[3,4,2], 'min_samples_split':[11,9,13], 'subsample':[.53,.55,.57]}
        #-1.5793 1000, depth:4, leaf:13, split:8, sub:.33
        lc_test_params = {'min_samples_leaf':[15,17,13], 'max_depth':[3,4,5], 'min_samples_split':[4,6,8], 'subsample':[.35,.33,.37]}

        # print('grid_search_start')
        # grid_search(X_final_model, y_final_wins, final_wc_params, wc_test_params)
        # grid_search(X_final_model, y_final_losses, final_lc_params, lc_test_params)

        final_wc_model_fit = final_wc_model.fit(X_final_model, y_final_wins)
        final_lc_model_fit = final_lc_model.fit(X_final_model, y_final_losses)
        ### Fit Final Predict Model End ###

        ### Make Final Predictions and Output to Terminal Start ###
        final_prediction_details['wins_contr'] = final_wc_model_fit.predict(X_final_predict)
        final_prediction_details['losses_contr'] = final_lc_model_fit.predict(X_final_predict)
        final_prediction_details['value_contr'] = final_prediction_details['wins_contr'] + final_prediction_details['losses_contr']
        final_prediction_details['difference'] = final_prediction_details['wins_contr'] - final_prediction_details['losses_contr']


        # print(final_prediction_details.sort_values('wins_contr', ascending=False).reset_index(drop=True)[0:50])
        # print(final_prediction_details.sort_values('losses_contr', ascending=False)[0:50])
        # print(final_prediction_details.sort_values('difference', ascending=False)[0:50])

        X_final_team_predict = pd.DataFrame(columns=['team_season_id', 'top_3_w', 'top_3_l', 'top_6_w', 'top_6_l', 'top_9_w', 'top_9_l'])
        for team in final_prediction_details['team_season_id'].unique():
            current_team = final_prediction_details[final_prediction_details['team_season_id'] == team].sort_values('value_contr', ascending=False).reset_index(drop=True)
            # print(current_team)
            # print('Projected Wins: ' + str(current_team.loc[0:8,'wins_contr'].sum()))
            # print('Projected Losses: ' + str(current_team.loc[0:8,'losses_contr'].sum()))
        ### Make Final Predictions and Output to Terminal End###

        ### Create New Team Predictions DF ###
                # print(current_team)
            projected_top_3_wins = current_team.loc[0:3, 'wins_contr'].sum()
            projected_top_3_losses = current_team.loc[0:3, 'losses_contr'].sum() 
            projected_top_6_wins = current_team.loc[0:6, 'wins_contr'].sum()
            projected_top_6_losses = current_team.loc[0:6, 'losses_contr'].sum() 
            projected_top_9_wins = current_team.loc[0:9, 'wins_contr'].sum()
            projected_top_9_losses = current_team.loc[0:9, 'losses_contr'].sum() 

            X_final_team_predict.loc[len(X_final_team_predict)] = [team, projected_top_3_wins, projected_top_3_losses, projected_top_6_wins, projected_top_6_losses, projected_top_9_wins, projected_top_9_losses]

        X_final_team_predict_standardized = standardize(X_final_team_predict.iloc[:, 1:].to_numpy())
        for idx, column in enumerate(X_final_team_predict.columns[1:]):
            X_final_team_predict[column] = X_final_team_predict_standardized[:, idx]

        projected_record_df = pd.DataFrame()
        projected_record_df['team_season_id'] = X_final_team_predict['team_season_id'].tolist()
        projected_record_df['projected_wins'] = team_wins_model_fit.predict(X_final_team_predict.drop(columns='team_season_id'))
        projected_record_df['projected_losses'] = team_losses_model_fit.predict(X_final_team_predict.drop(columns='team_season_id'))
        projected_record_df['win_pct'] = projected_record_df['projected_wins'] / (projected_record_df['projected_wins'] + projected_record_df['projected_losses'])
        projected_record_df['game_adjustment_needed'] = 82 - projected_record_df['projected_wins'] - projected_record_df['projected_losses']
        projected_record_df['adjusted_wins'] = round(projected_record_df['projected_wins'] + (projected_record_df['game_adjustment_needed'] * projected_record_df['win_pct']), 0)
        projected_record_df['adjusted_losses'] = round(projected_record_df['projected_losses'] + (projected_record_df['game_adjustment_needed'] * (1 - projected_record_df['win_pct'])), 0)
        projected_record_df['closest_to_even'] = abs(.5 - projected_record_df['win_pct'])
        projected_record_df = projected_record_df.sort_values('closest_to_even').reset_index(drop=True)


        adjustment = 1230 - projected_record_df['projected_wins'].sum()
        projected_record_df['win_loss_final_adjustment'] = [math.ceil(adjustment / (idx + 30)) for idx in range(len(projected_record_df))]
        projected_record_df['final_wins'] = projected_record_df['adjusted_wins'] + projected_record_df['win_loss_final_adjustment']
        projected_record_df['final_losses'] = projected_record_df['adjusted_losses'] - projected_record_df['win_loss_final_adjustment']
        projected_record_df = projected_record_df.sort_values('final_wins', ascending=False).reset_index(drop=True)
        # print(projected_record_df)

        player_projections_2020_df = pd.DataFrame(columns=['player_name', 'player_season_id', 'team_season_id', 'wins_contr', 'losses_contr', 'val_contr', 'difference'])
        for idx in range(len(projected_record_df)):
            current_team_id = projected_record_df.loc[idx, 'team_season_id']
            current_team_players = final_prediction_details[final_prediction_details['team_season_id'] == current_team_id].sort_values('value_contr', ascending=False).reset_index(drop=True)
            current_team_player_wins = current_team_players['wins_contr'].sum()
            current_team_player_losses = current_team_players['losses_contr'].sum()

            for i in range(len(current_team_players)):
                pct_wins = current_team_players.loc[i, 'wins_contr'] / current_team_player_wins
                new_wins = projected_record_df.loc[idx, 'final_wins'] * pct_wins
                pct_losses = current_team_players.loc[i, 'losses_contr'] / current_team_player_losses
                new_losses = projected_record_df.loc[idx, 'final_losses'] * pct_losses
                total_val = new_wins + new_losses
                difference = new_wins - new_losses

                player_projections_2020_df.loc[len(player_projections_2020_df)] = [current_team_players.loc[i, 'player_name'], current_team_players.loc[i, 'player_season_id'],current_team_id, new_wins, new_losses, total_val, difference]

        # print('Adjusted Wins: ' + str(projected_record_df['adjusted_wins'].sum()))
        # print('Adjusted Losses: ' + str(projected_record_df['adjusted_losses'].sum()))
        # print('Total Wins: ' + str(projected_record_df['final_wins'].sum()))
        # print('Total Losses: ' + str(projected_record_df['final_losses'].sum()))
        print(player_projections_2020_df.sort_values('wins_contr', ascending=False)[0:50])
        print(projected_record_df.sort_values('final_wins', ascending=False)[0:50])
        # print(player_projections_2020_df.sort_values('val_contr', ascending=False)[0:50])
        # print(player_projections_2020_df.sort_values('difference', ascending=False)[0:50])

        for team in player_projections_2020_df['team_season_id'].unique():
            current_team = player_projections_2020_df[player_projections_2020_df['team_season_id'] == team].sort_values('val_contr', ascending=False).reset_index(drop=True)
            # print(current_team)

        team_projection_df = team_projection_df.append(projected_record_df)
        player_projection_df = player_projection_df.append(player_projections_2020_df)

    if injuries == 'yes':
        export_csv = team_projection_df.to_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/team_predictions_injuries_updated_' + str(n_estimators) + '_2020.csv')
        export_csv = player_projection_df.to_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/player_predictions_injuries_updated_' + str(n_estimators) + '_2020.csv')
    else:
        export_csv = team_projection_df.to_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/team_predictions_updated_' + str(n_estimators) + '_2020.csv')
        export_csv = player_projection_df.to_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/player_predictions_updated_' + str(n_estimators) + '_2020.csv')

    print(team_projection_df.groupby('team_season_id').mean().sort_values('final_wins', ascending=False)[0:50])
    print(player_projection_df.groupby(['player_season_id', 'player_name']).mean().sort_values('wins_contr', ascending=False)[0:50])

runs = 10

grouped_teams = group_players(team_similarity_df, .55, 'team_season_id', 2)
grouped_players = group_players(player_similarity_df, .6, 'id', 4)

# team_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_injured_excluded_aligned.csv')
# player_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/player_similarity_matrix_3.csv')

# initial_seasons_list = [2013,2014,2015,2016,2017,2018,2019]
# injured_players_list = ['Kevin Durant', 'DeMarcus Cousins', 'John Wall', 'Andre Iguodala', 'Darius Miller', 'Paul George', 'Victor Oladipo', 'Jusuf Nurkic', 'Klay Thompson']

# team_projection_df = pd.DataFrame()
# player_projection_df = pd.DataFrame()

predict_season(team_similarity_df, player_similarity_df, initial_seasons_list, injured_players_list, runs, team_projection_df, player_projection_df, 1000, 'yes', grouped_teams, grouped_players)

# team_projection_df = pd.DataFrame()
# player_projection_df = pd.DataFrame()

# team_similarity_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/similarity_analysis/team_similarity_matrix_2020_aligned.csv')

# injured_players_list = ['Kevin Durant', 'DeMarcus Cousins', 'John Wall', 'Andre Iguodala', 'Darius Miller']

# predict_season(team_similarity_df, player_similarity_df, initial_seasons_list, injured_players_list, runs, team_projection_df, player_projection_df, 1000, 'no')

players_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/player_predictions_injuries_1000_2020.csv').drop(columns='Unnamed: 0')
teams_df = pd.read_csv('/Users/jacobpress/Projects/wins_contributed/new_prediction/team_predictions_injuries_1000_2020.csv').drop(columns='Unnamed: 0')
print(players_df.groupby(['player_season_id', 'player_name']).mean().sort_values('wins_contr', ascending=False)[0:50])
print(teams_df.groupby(['team_season_id']).mean().sort_values('final_wins', ascending=False)[0:50])

# print(review_df)
# for team in review_df['team_season_id'].unique():
#     current_team = review_df[review_df['team_season_id'] == team]
#     current_team = current_team.groupby(['player_season_id', 'player_name']).mean().sort_values('wins_contr', ascending=False)
#     print(current_team)
