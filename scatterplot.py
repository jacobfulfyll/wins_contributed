import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from time import sleep
from classes.teamgamelog import TeamGameLog
import random
import numpy as np

conn = pg2.connect(dbname= "jacob_wins", host = "localhost")
cur = conn.cursor()
# SQL Pull
season_sort = """SELECT team_id,
                        player_id,
                        player_name,
                        SUM(wins_contr) AS TOTAL_WINS,
                        AVG(wins_contr) AS PER_WIN,
                        MAX(wins_contr) AS Max_Game
                 FROM jacob_wins_2019_final
                 GROUP BY player_id, player_name, team_id
                 ORDER BY Max_Game DESC"""

                                                  

season_df = pd.read_sql(season_sort, con=conn)
print(season_df)
conn.close()

rand_players = random.sample(range(11, int(len(season_df)-len(season_df)*.5)), 5) + list(range(10))
# Top 15 and 5 random labels #### random.sample(range(16, int(len(season_df)-len(season_df)*.5)), 5) + list(range(15))

sns.set(rc={'figure.figsize':(20,15)})
p1 = sns.scatterplot(x="per_win", y="total_wins", data=season_df, hue='max_game', alpha=.5)

for player in rand_players:
    df = season_df[season_df.index == player]
    name = df.loc[player]['player_name']
    df = df.reset_index()
    x = df.loc[0]['per_win']
    y = df.loc[0]['total_wins']
    z = df.loc[0]["max_game"]
    x_adj = random.uniform(-.001, .001)
    y_adj = random.uniform(-.001, .001)
    p1.text(x+x_adj, y+y_adj, name + ' ('+str(round(z, 2))+')', horizontalalignment='left', size=6, color='black')
plt.xlabel('Average Per Win')
plt.ylabel('Total Wins')
plt.legend(loc='upper left')
plt.title("2018-19 Season")
filepath = 'Graphs/Season_Scatters/2018-19'
plt.savefig(filepath)
plt.show()