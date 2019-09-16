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
'''
conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()
# SQL Pull
multi_season_sort = """SELECT team_id,
                        player_id,
                        player_name,
                        SUM(wins_contr) AS TOTAL_WINS,
                        AVG(wins_contr) AS PER_WIN,
                        MAX(wins_contr) AS MAX_WIN
                        FROM(
                                SELECT *
                                FROM reg_season_2013_14
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2014_15
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2015_16
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2016_17
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2017_18
                                
                                UNION ALL

                                SELECT *
                                FROM reg_season_2018_19) t
                 WHERE t.win_loss = 1
                 GROUP BY player_id, player_name, team_id
                 ORDER BY PER_WIN DESC"""

single_season_sort = """SELECT team_id,
                        player_id,
                        player_name,
                        SUM(wins_contr) AS TOTAL_WINS,
                        AVG(wins_contr) AS PER_WIN,
                        MAX(wins_contr) AS MAX_WIN
                        FROM reg_season_2018_19
                        WHERE win_loss = 1
                        GROUP BY player_id, player_name, team_id
                        ORDER BY PER_WIN DESC"""

teams = teams_dict()
#
#random.sample(range(16, int(len(season_df)-len(season_df)*.5)), 5) + list(range(15))
 

for team in teams:
    team_id = team.get('teamId')
    team_name = team.get('teamName')
    team_colors = team.get('colors')
    save_name = team.get('teamName').lower().replace(' ', '_')
    save_name = save_name + '_reg_season'
    print(save_name)
    season_df = pd.read_sql(single_season_sort, con=conn)
    season_df = season_df[season_df['team_id'] == team_id]
    season_df = season_df.reset_index()
    rand_players = range(len(season_df))
    filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2018_19/' + save_name
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
    ax.set_xlabel('Average Per Win', fontname="Oswald", fontsize=14, fontweight=600)
    ax.set_ylabel('Total Wins', fontname="Oswald", fontsize=14, fontweight=600)
    ax.xaxis.label.set_color('#4b86b4')
    ax.yaxis.label.set_color('#4b86b4')
    for tick in ax.get_xticklabels():
        tick.set_fontname("Roboto")
    for tick in ax.get_yticklabels():
        tick.set_fontname("Roboto")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.title('2018-19 Regular Season')
    plt.savefig(filepath)
    plt.show()

conn.close()

## What To Change

# FROM IN SQL STATEMENT : CHANGE YEAR : LINE 22
# Single sort or multi-sort : CHANGE VARIABLE IN LINE 76
# FILE PATH LOCATION : CHANGE YEAR : LINE 80
'''
def reg_season_2013_14_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2013_14
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2013_14/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2013-14 Regular Season Losses')
            else:
                plt.title('2013-14 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def reg_season_2014_15_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2014_15
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2014_15/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2014-15 Regular Season Losses')
            else:
                plt.title('2014-15 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def reg_season_2015_16_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2015_16
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2015_16/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2015-16 Regular Season Losses')
            else:
                plt.title('2015-16 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def reg_season_2016_17_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2016_17
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2016_17/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2016-17 Regular Season Losses')
            else:
                plt.title('2016-17 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def reg_season_2017_18_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2017_18
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2017_18/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2017-18 Regular Season Losses')
            else:
                plt.title('2017-18 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def reg_season_2018_19_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM reg_season_2018_19
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_reg_season_losses'
            else:
                save_name = save_name + '_reg_season_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2018_19/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2018-19 Regular Season Losses')
            else:
                plt.title('2018-19 Regular Season Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2013_14_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2013_14
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2013_14/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2013-14 Playoffs Losses')
            else:
                plt.title('2013-14 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2014_15_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2014_15
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2014_15/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2014-15 Playoffs Losses')
            else:
                plt.title('2014-15 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2015_16_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2015_16
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2015_16/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2015-16 Playoffs Losses')
            else:
                plt.title('2015-16 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2016_17_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2016_17
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2016_17/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2016-17 Playoffs Losses')
            else:
                plt.title('2016-17 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2017_18_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2017_18
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2017_18/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2017-18 Playoffs Losses')
            else:
                plt.title('2017-18 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()

def playoffs_2018_19_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        single_season_sort = """SELECT team_id,
                            player_id,
                            player_name,
                            SUM(wins_contr) AS TOTAL_WINS,
                            AVG(wins_contr) AS PER_WIN,
                            MAX(wins_contr) AS MAX_WIN
                            FROM playoffs_2018_19
                            WHERE win_loss = %(win_loss)s
                            GROUP BY player_id, player_name, team_id
                            ORDER BY PER_WIN DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = save_name + '_playoffs_losses'
            else:
                save_name = save_name + '_playoffs_wins'
            print(save_name)
            season_df = pd.read_sql(single_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/2018_19/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2018-19 Playoffs Losses')
            else:
                plt.title('2018-19 Playoffs Wins')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()


def run_all_team_scatters():
    reg_season_2013_14_team_scatters()
    reg_season_2014_15_team_scatters()
    reg_season_2015_16_team_scatters()
    reg_season_2016_17_team_scatters()
    reg_season_2017_18_team_scatters()
    reg_season_2018_19_team_scatters()
    playoffs_2013_14_team_scatters()
    playoffs_2014_15_team_scatters()
    playoffs_2015_16_team_scatters()
    playoffs_2016_17_team_scatters()
    playoffs_2017_18_team_scatters()
    playoffs_2018_19_team_scatters()

#run_all_team_scatters()


def all_time_team_scatters():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    for win_loss in range(2):
        multi_season_sort = """SELECT team_id,
                                player_id,
                                player_name,
                                SUM(wins_contr) AS TOTAL_WINS,
                                AVG(wins_contr) AS PER_WIN,
                                MAX(wins_contr) AS MAX_WIN
                                FROM(
                                        SELECT *
                                        FROM reg_season_2013_14
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM reg_season_2014_15
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM reg_season_2015_16
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM reg_season_2016_17
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM reg_season_2017_18
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM reg_season_2018_19
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2013_14
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2014_15
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2015_16
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2016_17
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2017_18
                                        
                                        UNION ALL

                                        SELECT *
                                        FROM playoffs_2018_19) t
                        WHERE t.win_loss = %(win_loss)s
                        GROUP BY t.player_id, t.player_name, t.team_id
                        ORDER BY TOTAL_WINS DESC"""

        teams = teams_dict()

        for team in teams:
            team_id = team.get('teamId')
            team_colors = team.get('colors')
            save_name = team.get('teamName').lower().replace(' ', '_')
            if win_loss == 0:
                save_name = 'all_time_wc_il/' + save_name
            else:
                save_name = 'all_time_wc/' + save_name
            print(save_name)
            season_df = pd.read_sql(multi_season_sort, con=conn, params={'win_loss': win_loss})
            season_df = season_df[season_df['team_id'] == team_id]
            season_df = season_df.reset_index()
            rand_players = range(len(season_df))
            filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_scatters/' + save_name
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
            ax.set_xlabel('Average Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.set_ylabel('Total Contributed', fontname="Oswald", fontsize=14, fontweight=600)
            ax.xaxis.label.set_color('#4b86b4')
            ax.yaxis.label.set_color('#4b86b4')
            for tick in ax.get_xticklabels():
                tick.set_fontname("Roboto")
            for tick in ax.get_yticklabels():
                tick.set_fontname("Roboto")

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if win_loss == 0:
                plt.title('2013-19 Wins Contributed (Losses)')
            else:
                plt.title('2013-19 Wins Contributed (Wins)')
            plt.savefig(filepath)
            print('graph_saved')

    conn.close()    

all_time_team_scatters()