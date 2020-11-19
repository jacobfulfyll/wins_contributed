from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams
import pandas as pd
import psycopg2 as pg2
from sqlalchemy import create_engine
import numpy as np
from time import sleep



def add_one_team_to_league_df(team_id, season_end):

    team_info = teams.find_team_name_by_id(team_id)
    team_name = team_info.get('full_name')
    print(team_name + '' +str(team_id))
    team_roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season_end).common_team_roster.get_data_frame()
    team_df = team_roster[['PLAYER_ID', 'TeamID', 'SEASON', 'PLAYER', 'AGE', 'EXP']]
    team_df = team_df.rename(columns={'PLAYER_ID':'player_id', 'TeamID':'team_id', 'SEASON':'season_end', 'PLAYER':'player_name', 'AGE':'age', 'EXP':'exp'})
    team_df['team_name'] = team_name
    #league_df = league_df.append(team_df)

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    team_df.to_sql('league_rosters', con = engine, if_exists='append', index=False)
    conn.close()

#add_one_team_to_league_df(1610612764)


def create_league_team_df():

    team_ids = [1610612737, 1610612738, 1610612751, 1610612766, 1610612741, 1610612739, 1610612742, 
            1610612743, 1610612765, 1610612744, 1610612745, 1610612754, 1610612746, 1610612747, 
            1610612763, 1610612748, 1610612749, 1610612750, 1610612740, 1610612752, 1610612760, 
            1610612753, 1610612755, 1610612756, 1610612757, 1610612758, 1610612759, 1610612761, 
            1610612762, 1610612764]
    
    season_end_list = [2019, 2018, 2017, 2016, 2015, 2014]

    for season_end in season_end_list:
        for team_id in team_ids:
            team_info = teams.find_team_name_by_id(team_id)
            team_name = team_info.get('full_name')
            print(team_name + '' +str(team_id))
            team_roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season_end).common_team_roster.get_data_frame()
            team_df = team_roster[['PLAYER_ID', 'TeamID', 'SEASON', 'PLAYER', 'AGE', 'EXP']]
            team_df = team_df.rename(columns={'PLAYER_ID':'player_id', 'TeamID':'team_id', 'SEASON':'season_end', 'PLAYER':'player_name', 'AGE':'age', 'EXP':'exp'})
            team_df['team_name'] = team_name
            #league_df = league_df.append(team_df)

            conn = pg2.connect(dbname = 'postgres', host = "localhost")
            conn.autocommit = True
            engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
            team_df.to_sql('league_rosters', con = engine, if_exists='append', index=False)
            conn.close()

            sleep(15)

# create_league_team_df()

def fix_player_ages_exp():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor() 

    age_exp_query = """SELECT *
                        FROM league_rosters;"""
    
    age_exp_df = pd.read_sql(age_exp_query, con=conn)

    age_exp_df['id'] = [str(age_exp_df.loc[x, 'player_id']) + '_' + str(age_exp_df.loc[x, 'season_end']) for x in range(len(age_exp_df))]
    age_exp_df['age'] = age_exp_df['age'].astype(float)
    age_exp_df = age_exp_df.sort_values(by=['player_id', 'season_end']).reset_index(drop=True)

    for idx in range(len(age_exp_df)):
        if idx == 0:
            age_exp_df.loc[idx, 'age'] = age_exp_df.loc[idx, 'age'] - 1
        elif age_exp_df.loc[idx-1, 'player_id'] == age_exp_df.loc[idx, 'player_id']:
            age_exp_df.loc[idx, 'age'] = age_exp_df.loc[idx - 1, 'age'] + 1
        else:
            age_exp_df.loc[idx, 'age'] = age_exp_df.loc[idx, 'age'] - 1

        if age_exp_df.loc[idx, 'exp'] == 'R':
            age_exp_df.loc[idx, 'exp'] = 0
        else:
            pass

    age_exp_df['exp'] = age_exp_df['exp'].astype(float)

    print(age_exp_df[age_exp_df['player_name'] == "D'Angelo Russell"])

    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    age_exp_df.to_sql('age_exp', con = engine, if_exists='replace', index=False)
    conn.close()


#fix_player_ages_exp()

def create_2020_rosters():

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor() 

    roster_query = """SELECT *
                        FROM league_rosters
                        WHERE season_end = '2019';"""
    
    roster_df = pd.read_sql(roster_query, con=conn)

    print(roster_df)

create_2020_rosters()

