import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from time import sleep
import random
import numpy as np


def league_scatter():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    # SQL Pull
    season_sort = """SELECT player_id,
                            player_name,
                            SUM(value_contributed) AS TOTAL_CONTR,
                            AVG(value_contributed) AS PER_GAME,
                            MAX(value_contributed) AS MAX_GAME
                    FROM value_contributed_2019_20
                    WHERE win_loss = 1
                    AND season_type = 'Regular Season'
                    GROUP BY player_id, player_name
                    ORDER BY Max_Game DESC"""
        

    season_df = pd.read_sql(season_sort, con=conn)
    print(season_df)
    conn.close()

    players = [0,1,2,3,4,5,6,7,8,9] #These represent the highest max games
    per_game = season_df.sort_values(by='per_game', ascending=False).index[0:10]
    total_contr = season_df.sort_values(by='total_contr', ascending=False).index[0:10]
    per_game = per_game.tolist()
    total_contr = total_contr.tolist()

    print(players)
    for p in (per_game + total_contr):
        #print(p)
        if p in players:
            continue
        else:
            players.append(p)

    print(players)

    #rand_players = random.sample(range(11, int(len(season_df)-len(season_df)*.5)), 5) + list(range(10))
    # Top 15 and 5 random labels #### random.sample(range(16, int(len(season_df)-len(season_df)*.5)), 5) + list(range(15))
    
    sns.set(rc={'figure.figsize':(8,5)})
    p1 = sns.scatterplot(x="per_game", y="total_contr", data=season_df, hue='max_game', alpha=.5)
    y_max = p1.get_ylim()[1]
    y_min = p1.get_ylim()[0]
    x_max = p1.get_xlim()[1]
    x_min = p1.get_xlim()[0]
    print(x_min)
    print(x_max)
    print(y_min)
    print(y_max)
    character_width = 0.010903216584521756 * (x_max - x_min)
    character_height = 0.023 * (y_max - y_min)

    x_vectors = []
    y_vectors = []

    for player in players:
        df = season_df[season_df.index == player]
        name = df.loc[player]['player_name']

        x_adj = .0015 * (x_max - x_min)
        y_adj = .0034 * (y_max - y_min)

        df = df.reset_index()
        x = df.loc[0]['per_game']
        y = df.loc[0]['total_contr']
        z = df.loc[0]["max_game"]

        x_start = x + x_adj
        y_start = y + y_adj

        x_end = x_start + ((len(name) + 5) * character_width)
        y_end = y_start + character_height

        x_range = [x_start, x_end]
        y_range = [y_start, y_end]

        intersect = 0

        for idx in range(len(x_vectors)):
            if ( (x_start <= x_vectors[idx][0] <= x_end or x_start <= x_vectors[idx][1] <= x_end or x_vectors[idx][0] <= x_start <= x_vectors[idx][1] or x_vectors[idx][0] <= x_end <= x_vectors[idx][1]) 
                and (y_start <= y_vectors[idx][0] <= y_end or y_start <= y_vectors[idx][1] <= y_end or y_vectors[idx][0] <= y_start <= y_vectors[idx][1] or y_vectors[idx][0] <= y_end <= y_vectors[idx][1]) ):
                intersect = 1
                break
            else:
                continue
        if intersect == 0:
            x_vectors.append(x_range)
            y_vectors.append(y_range)
            p1.text(x_start, y_start, name + ' ('+str(round(z, 2))+')', horizontalalignment='left', size=6, color='black')
        else:
            continue

    sample_size = int(len(season_df))
    #print(sample_size)
    #sleep(2)
    player_count = 0
    checked_list = []
    while player_count <= sample_size - 1:
        player = random.sample(range(sample_size), 1)[0]
        if player in checked_list:
            continue
        #print(player)
        #print('count: ' + str(player_count))
        #sleep(1)
        df = season_df.sort_values(by='per_game', ascending=False).reset_index(drop=True)
        df = df[df.index == player]
        name = df.loc[player]['player_name']

        x_adj = .0015 * (x_max - x_min)
        y_adj = .0034 * (y_max - y_min)

        df = df.reset_index()
        x = df.loc[0]['per_game']
        y = df.loc[0]['total_contr']
        z = df.loc[0]["max_game"]

        x_start = x + x_adj
        y_start = y + y_adj

        x_end = x_start + ((len(name) + 5) * character_width)
        y_end = y_start + character_height

        x_range = [x_start, x_end]
        y_range = [y_start, y_end]

        intersect = 0

        for idx in range(len(x_vectors)):
            if ( (x_start <= x_vectors[idx][0] <= x_end or x_start <= x_vectors[idx][1] <= x_end or x_vectors[idx][0] <= x_start <= x_vectors[idx][1] or x_vectors[idx][0] <= x_end <= x_vectors[idx][1]) 
                and (y_start <= y_vectors[idx][0] <= y_end or y_start <= y_vectors[idx][1] <= y_end or y_vectors[idx][0] <= y_start <= y_vectors[idx][1] or y_vectors[idx][0] <= y_end <= y_vectors[idx][1]) ):
                intersect = 1
                break
            else:
                continue
        if intersect == 0:
            player_count += 1
            checked_list.append(player)
            x_vectors.append(x_range)
            y_vectors.append(y_range)
            p1.text(x_start, y_start, name + ' ('+str(round(z, 2))+')', horizontalalignment='left', size=6, color='black')
        else:
            checked_list.append(player)
            player_count += 1
            continue
    
    plt.xlabel('Per Game Contributed')
    plt.ylabel('Total Contributed')
    plt.legend(loc='upper left')
    plt.title("2018-19 Playoffs Wins Contributed", fontsize=16)
    
    # filepath = '/Users/jacobpress/Desktop/website_s3/value_contr/league_scatterplots/wins_contr/playoffs_2018_19.png'
    # plt.savefig(filepath)
    plt.show()



league_scatter()



## What To Change

# FROM IN SQL STATEMENT : CHANGE YEAR : LINE 20
# FILE PATH LOCATION : CHANGE YEAR : LINE 50
# GRAPH TITLE : CHANGE YEAR : LINE 49
"""SELECT player_id,
                            player_name,
                            SUM(value_contributed) AS TOTAL_CONTR,
                            AVG(value_contributed) AS PER_GAME,
                            MAX(value_contributed) AS MAX_GAME
                            FROM(                            
                                SELECT *
                                FROM value_contributed_2013_14
                                
                                UNION ALL

                                SELECT *
                                FROM value_contributed_2014_15
                                
                                UNION ALL

                                SELECT *
                                FROM value_contributed_2015_16
                                
                                UNION ALL

                                SELECT *
                                FROM value_contributed_2016_17
                                
                                UNION ALL

                                SELECT *
                                FROM value_contributed_2017_18
                                
                                UNION ALL

                                SELECT *
                                FROM value_contributed_2018_19) t
                    where win_loss = 1
                    GROUP BY t.player_id, t.player_name
                    ORDER BY Max_Game DESC"""