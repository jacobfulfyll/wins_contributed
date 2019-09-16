from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams
import pandas as pd
import psycopg2 as pg2
from sqlalchemy import create_engine
import numpy as np



def add_one_team_to_league_df(team_id):

    team_info = teams.find_team_name_by_id(team_id)
    team_name = team_info.get('full_name')
    print(team_name + '' +str(team_id))
    team_roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=2019).common_team_roster.get_data_frame()
    team_df = team_roster[['PLAYER_ID', 'TeamID', 'SEASON', 'PLAYER', 'AGE', 'EXP']]
    team_df = team_df.rename(columns={'PLAYER_ID':'player_id', 'TeamID':'team_id', 'SEASON':'season_end', 'PLAYER':'player_name', 'AGE':'age', 'EXP':'exp'})
    team_df['team_name'] = team_name
    #league_df = league_df.append(team_df)

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    team_df.to_sql('league_teams_2020', con = engine, if_exists='append', index=False)
    conn.close()

#add_one_team_to_league_df(1610612764)


def create_league_team_df():

    team_ids = [1610612737, 1610612738, 1610612751, 1610612766, 1610612741, 1610612739, 1610612742, 
            1610612743, 1610612765, 1610612744, 1610612745, 1610612754, 1610612746, 1610612747, 
            1610612763, 1610612748, 1610612749, 1610612750, 1610612740, 1610612752, 1610612760, 
            1610612753, 1610612755, 1610612756, 1610612757, 1610612758, 1610612759, 1610612761, 
            1610612762, 1610612764]

    league_df = pd.DataFrame()
    for team_id in team_ids:
        team_info = teams.find_team_name_by_id(team_id)
        team_name = team_info.get('full_name')
        print(team_name + '' +str(team_id))
        team_roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=2019).common_team_roster.get_data_frame()
        team_df = team_roster[['PLAYER_ID', 'TeamID', 'SEASON', 'PLAYER', 'AGE', 'EXP']]
        team_df = team_df.rename(columns={'PLAYER_ID':'player_id', 'TeamID':'team_id', 'SEASON':'season_end', 'PLAYER':'player_name', 'AGE':'age', 'EXP':'exp'})
        team_df['team_name'] = team_name
        #league_df = league_df.append(team_df)

        conn = pg2.connect(dbname = 'postgres', host = "localhost")
        conn.autocommit = True
        engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
        team_df.to_sql('league_teams_2020', con = engine, if_exists='append', index=False)
        conn.close()

#create_league_team_df()


def team_predictions():

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    predictions_2020 = """SELECT *
                        FROM player_projections_2020"""

    league_2020 = """SELECT * FROM league_teams_2020"""

    
    prediction_df = pd.read_sql(predictions_2020, con=conn)
    league_df = pd.read_sql(league_2020, con=conn)
    team_predictions_df = pd.merge(prediction_df, league_df,on=['player_id', 'player_name'])
    team_predictions_df = team_predictions_df.groupby(['team_id', 'team_name'], as_index=False).sum()

    team_predictions_df['wins_normalized'] = team_predictions_df['wins_contr'] / (team_predictions_df['wins_contr'] + team_predictions_df['wins_contr_in_loss']) * 82
    team_predictions_df['losses_normalized'] = team_predictions_df['wins_contr_in_loss'] / (team_predictions_df['wins_contr'] + team_predictions_df['wins_contr_in_loss']) * 82
    team_predictions_df['loss_contr_guess'] = [82 - x for idx, x in team_predictions_df['wins_contr'].iteritems()]
    team_predictions_df['w_l_ratio_sqrd'] = (team_predictions_df['wins_contr'] / team_predictions_df['wins_contr_in_loss']) ** 2
    ratio_sum = np.sum(team_predictions_df['w_l_ratio_sqrd'])
    print(ratio_sum)
    excess_deficiency = (np.sum(team_predictions_df['loss_contr_guess']) - np.sum(team_predictions_df['wins_contr'])) / 2

    team_predictions_df['win_adjustment_factor'] = [x / ratio_sum for idx, x in team_predictions_df['w_l_ratio_sqrd'].iteritems()]
    team_predictions_df['win_adjustment'] = team_predictions_df['win_adjustment_factor'] * excess_deficiency
    team_predictions_df['final_wins'] = team_predictions_df['wins_contr'] + team_predictions_df['win_adjustment']
    team_predictions_df['final_wins_rounded'] = [round(x) for idx, x in team_predictions_df['final_wins'].iteritems()]
    team_predictions_df['final_losses_rounded'] = 82 - team_predictions_df['final_wins_rounded']
    team_predictions_df['season_end'] = 2020
    conn.close()
    print(team_predictions_df.sort_values('final_wins'))

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    team_predictions_df.to_sql('team_projected_records', con = engine, if_exists='replace', index=False)
    
    conn.close()

    
team_predictions()

def adjust_player_projections():

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    league = """SELECT * FROM league_teams_2020"""

    player_predictions = """SELECT *
                        FROM player_projections_2020"""

    team_predictions = """SELECT team_id, wins_contr as team_wins_contr, wins_contr_in_loss as team_wc_il, final_wins_rounded, final_losses_rounded
                        FROM team_projected_records"""

    players_df = pd.read_sql(player_predictions, con=conn)
    league_df = pd.read_sql(league, con=conn)
    teams_df = pd.read_sql(team_predictions, con=conn)

    updated_projections_df = pd.merge(players_df, league_df[['player_id', 'team_id']], on='player_id')
    updated_projections_df = pd.merge(updated_projections_df, teams_df, on='team_id')

    updated_projections_df['final_player_wins'] = updated_projections_df['wins_contr'] / updated_projections_df['team_wins_contr'] * updated_projections_df['final_wins_rounded']
    updated_projections_df['final_player_losses'] = updated_projections_df['wins_contr_in_loss'] / updated_projections_df['team_wc_il'] * updated_projections_df['final_losses_rounded']

    updated_projections_df = updated_projections_df.sort_values('final_player_wins', ascending=False)
    print(updated_projections_df)
    
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    updated_projections_df.to_sql('player_projections_2020_updated', con = engine, if_exists='replace', index=False)

adjust_player_projections()



