import psycopg2 as pg2
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.pyplot as plt
import copy
from time import sleep
from classes.teamgamelog import TeamGameLog
import random
import numpy as np
from classes.teams import teams_dict

conn = pg2.connect(dbname= "jacob_wins", host = "localhost")
cur = conn.cursor()
# SQL Pull
season_sort = """SELECT team_id,
                        player_id,
                        player_name,
                        SUM(wins_contr) AS TOTAL_WINS,
                        AVG(wins_contr) AS PER_WIN,
                        MAX(wins_contr) AS MAX_WIN
                 FROM jacob_wins_2018_final
                 GROUP BY player_id, player_name, team_id
                 ORDER BY PER_WIN DESC"""


teams = teams_dict()
#
#random.sample(range(16, int(len(season_df)-len(season_df)*.5)), 5) + list(range(15))
 

for team in teams:
    team_id = team.get('teamId')
    team_name = team.get('teamName')
    team_colors = team.get('colors')
    simple_name = team.get('simpleName')
    season_df = pd.read_sql(season_sort, con=conn)
    season_df = season_df[season_df['team_id'] == team_id]
    season_df = season_df.reset_index()
    rand_players = range(len(season_df))
    filepath = 'Graphs/Team_Scatters/2017-18/' + simple_name
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i, player in enumerate(rand_players):
        name = season_df.loc[player]['player_name']
        x = season_df.loc[i]['per_win']
        y = season_df.loc[i]['total_wins']
        z = season_df.loc[i]["max_win"]
        #x_adj = random.uniform(-.001, .001)
        #y_adj = random.uniform(-.001, .001)
        ax.scatter(x, y, color=team_colors[random.randint(0, len(team_colors)-1)], alpha=.7)
        ax.text(x, y, name+'('+str(round(z, 2))+')', fontsize=6)
    ax.set_xlabel('Average Per Win')
    ax.set_ylabel('Total Wins')
    plt.title(team_name)
    plt.savefig(filepath)
    plt.show()

conn.close()

## What To Change

# FROM IN SQL STATEMENT : CHANGE YEAR : LINE 22
# FILE PATH LOCATION : CHANGE YEAR : LINE 41