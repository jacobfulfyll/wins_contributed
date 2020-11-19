import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import copy
import random
import numpy as np
import plotly.graph_objects as go
from teams import teams_dict

conn = pg2.connect(dbname= "personal_website", host = "localhost")
cur = conn.cursor()

teams_query = """SELECT team_id, team_name_link
                    FROM nba_teams;"""

teams_df = pd.read_sql(teams_query, con=conn)

conn.close()

def cumulative_team(team_id, team_name_link):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    playoffs_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val
                        FROM all_seasons_value_contributed
                        WHERE team_id = %(team_id)s
                        AND season_type = 'Playoffs'
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    reg_season_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val
                        FROM all_seasons_value_contributed
                        WHERE team_id = %(team_id)s
                        AND season_type = 'Regular Season'
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    playoffs_df = pd.read_sql(playoffs_query, con=conn, params={'team_id': int(team_id)})
    reg_season_df = pd.read_sql(reg_season_query, con=conn, params={'team_id': int(team_id)})
    conn.close()
    
    teams = teams_dict()
    playoffs_df['color'] = [teams[team_id].get('colors')[0] if win_loss == 0 else teams[team_id].get('colors')[1] for idx, win_loss in playoffs_df['win_loss'].iteritems()]
    reg_season_df['color'] = [teams[team_id].get('colors')[0] if win_loss == 0 else teams[team_id].get('colors')[1] for idx, win_loss in reg_season_df['win_loss'].iteritems()]


    # fig = plt.figure(figsize=(800/192, 800/192), dpi=192)
    fig, (ax1, ax2) = plt.subplots(2, figsize=(567/192, 500/192), dpi=192)

    ax1.scatter(reg_season_df['avg_val'], reg_season_df['total_val'], color=reg_season_df['color'], alpha=.4, s=4, edgecolors='none')
    ax2.scatter(playoffs_df['avg_val'], playoffs_df['total_val'], color=playoffs_df['color'], alpha=.4, s=4, edgecolors='none')
    # ax1.set_xticklabels({'fontsize':'10px'})
    plt.xlabel('Value Contributed (Per Game)', fontsize=6)
    ax1.set_ylabel('Regular Season', fontsize=4)
    ax2.set_ylabel('Playoffs Total', fontsize=4)

    ax1.tick_params(axis='both',labelsize=4, length=2, width=.5)
    ax2.tick_params(axis='both',labelsize=4, length=2, width=.5)

    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Win', markerfacecolor=teams[team_id].get('colors')[1], markersize=2, alpha=.4, markeredgewidth=0.0),
                    Line2D([0], [0], marker='o', color='w', label='Loss', markerfacecolor=teams[team_id].get('colors')[0], markersize=2, alpha=.4, markeredgewidth=0.0)]

    # Create the figure
    ax1.legend(handles=legend_elements, loc=2, prop={'size': 4})

    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # handles, labels = ax1.get_legend_handles_labels()
    # ax1.legend(handles, labels, loc=2, )



    df_list = [reg_season_df, playoffs_df]
    ax_list = [ax1, ax2]
    for i, ax in enumerate(ax_list):
        #print(sample_size)
        #sleep(2)
        y_max = ax.get_ylim()[1]
        y_min = ax.get_ylim()[0]
        x_max = ax.get_xlim()[1]
        x_min = ax.get_xlim()[0]
        
        character_width = 0.011903216584521756 * (x_max - x_min)
        character_height = 0.024 * (y_max - y_min)  

        x_vectors = []
        y_vectors = []
        sample_size = int(len(df_list[i]))
        player_count = 0
        checked_list = []
        while player_count <= sample_size - 1:
            player = random.sample(range(sample_size), 1)[0]
            if player in checked_list:
                continue
            #print(player)
            #print('count: ' + str(player_count))
            #sleep(1)
            df = df_list[i].sort_values(by='avg_val', ascending=False).reset_index(drop=True)
            df = df[df.index == player]
            name = df.loc[player]['player_name']

            x_adj = .0015 * (x_max - x_min)
            y_adj = .0034 * (y_max - y_min)

            df = df.reset_index()
            x = df.loc[0]['avg_val']
            y = df.loc[0]['total_val']

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
                ax.text(x_start, y_start, name, horizontalalignment='left', size=3, color='black')
            else:
                checked_list.append(player)
                player_count += 1
                continue


    print('Team Cumulative: ', team_name_link)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/team_graphs/team_cum/cum_' + team_name_link + '.png'
    plt.savefig(filepath)

    # plt.show()
    plt.close()

# for idx in range(len(teams_df)):
#     team_id = teams_df.loc[idx, 'team_id']
#     team_name_link = teams_df.loc[idx, 'team_name_link']
#     cumulative_team(team_id, team_name_link)  


def yearly_team(team_id, team_name_link, season_end):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    playoffs_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val
                        FROM all_seasons_value_contributed
                        WHERE team_id = %(team_id)s
                        AND season_type = 'Playoffs'
                        AND season_end = %(season_end)s
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    reg_season_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val
                        FROM all_seasons_value_contributed
                        WHERE team_id = %(team_id)s
                        AND season_type = 'Regular Season'
                        AND season_end = %(season_end)s
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    playoffs_df = pd.read_sql(playoffs_query, con=conn, params={'team_id': int(team_id), 'season_end': season_end})
    reg_season_df = pd.read_sql(reg_season_query, con=conn, params={'team_id': int(team_id), 'season_end': season_end})
    conn.close()

    teams = teams_dict()
    playoffs_df['color'] = [teams[team_id].get('colors')[0] if win_loss == 0 else teams[team_id].get('colors')[1] for idx, win_loss in playoffs_df['win_loss'].iteritems()]
    reg_season_df['color'] = [teams[team_id].get('colors')[0] if win_loss == 0 else teams[team_id].get('colors')[1] for idx, win_loss in reg_season_df['win_loss'].iteritems()]


    # fig = plt.figure(figsize=(800/192, 800/192), dpi=192)
    fig, (ax1, ax2) = plt.subplots(2, figsize=(567/192, 500/192), dpi=192)
    rand_players = range(len(playoffs_df))
    ax1.scatter(reg_season_df['avg_val'], reg_season_df['total_val'], color=reg_season_df['color'], alpha=.4, s=4, edgecolors='none')
    ax2.scatter(playoffs_df['avg_val'], playoffs_df['total_val'], color=playoffs_df['color'], alpha=.4, s=4, edgecolors='none')
    # ax1.set_xticklabels({'fontsize':'10px'})
    plt.xlabel('Value Contributed (Per Game)', fontsize=6)
    ax1.set_ylabel('Regular Season Total Value', fontsize=4)
    ax2.set_ylabel('Playoffs Total Value', fontsize=4)

    ax1.tick_params(axis='both',labelsize=4, length=2, width=.5)
    ax2.tick_params(axis='both',labelsize=4, length=2, width=.5)

    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Win', markerfacecolor=teams[team_id].get('colors')[1], markersize=2, alpha=.4, markeredgewidth=0.0),
                    Line2D([0], [0], marker='o', color='w', label='Loss', markerfacecolor=teams[team_id].get('colors')[0], markersize=2, alpha=.4, markeredgewidth=0.0)]

    # Create the figure
    ax1.legend(handles=legend_elements, loc=2, prop={'size': 4})

    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # handles, labels = ax1.get_legend_handles_labels()
    # ax1.legend(handles, labels, loc=2, )



    df_list = [reg_season_df, playoffs_df]
    ax_list = [ax1, ax2]
    for i, ax in enumerate(ax_list):
        #print(sample_size)
        #sleep(2)
        y_max = ax.get_ylim()[1]
        y_min = ax.get_ylim()[0]
        x_max = ax.get_xlim()[1]
        x_min = ax.get_xlim()[0]
        
        character_width = 0.010903216584521756 * (x_max - x_min)
        character_height = 0.023 * (y_max - y_min)  

        x_vectors = []
        y_vectors = []
        sample_size = int(len(df_list[i]))
        player_count = 0
        checked_list = []
        while player_count <= sample_size - 1:
            player = random.sample(range(sample_size), 1)[0]
            if player in checked_list:
                continue
            #print(player)
            #print('count: ' + str(player_count))
            #sleep(1)
            df = df_list[i].sort_values(by='avg_val', ascending=False).reset_index(drop=True)
            df = df[df.index == player]
            name = df.loc[player]['player_name']

            x_adj = .0015 * (x_max - x_min)
            y_adj = .0034 * (y_max - y_min)

            df = df.reset_index()
            x = df.loc[0]['avg_val']
            y = df.loc[0]['total_val']

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
                ax.text(x_start, y_start, name, horizontalalignment='left', size=3, color='black')
            else:
                checked_list.append(player)
                player_count += 1
                continue


    print('Team Yearly: ', team_name_link + '_' + str(season_end))             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/team_graphs/team_yearly/' + str(season_end) + '_' + team_name_link + '.png'
    plt.savefig(filepath)

    # plt.show()
    plt.close()

# season_end_list = [2014,2015,2016,2017,2018,2019]
# for idx in range(len(teams_df)):
#     team_id = teams_df.loc[idx, 'team_id']
#     team_name_link = teams_df.loc[idx, 'team_name_link']
#     for season_end in season_end_list:
#         yearly_team(team_id, team_name_link, season_end)  


def projected_graph(team_id, team_name_link, team_season_id):

    conn = pg2.connect(dbname= "personal_website", host = "localhost")
    cur = conn.cursor()

    graph_query = """SELECT player_name, wins_contr as Win, losses_contr as Loss
                        FROM player_predictions
                        WHERE team_season_id = %(team_season_id)s;"""


    graph_df = pd.read_sql(graph_query, con=conn, params={'team_season_id':team_season_id})
    conn.close()

    teams = teams_dict()

    plt.figure(figsize=(8,8))
    graph_df = graph_df[0:10].melt('player_name', var_name='Outcome', value_name='vals')
    # print(graph_df)

    sns.set_style("white")
    sns.despine()
    sns.barplot(x='player_name', y='vals', hue='Outcome', data=graph_df, palette={'win':teams[team_id].get('colors')[1], 'loss':teams[team_id].get('colors')[0]}, saturation=.75)
    #plt.title(player_name_list[idx], fontsize=18)
    plt.ylabel('Value Contributed', fontsize=14)
    plt.xlabel('')
    sns.despine(offset=10, trim=True)
    plt.xticks(rotation=15, size=8)


    print('Player Career: ', team_name_link)              
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/team_graphs/team_projections/' + team_name_link + '.png'
    plt.savefig(filepath)
    plt.close()


# for idx in range(len(teams_df)):
#     team_id = teams_df.loc[idx, 'team_id'] 
#     team_season_id = str(team_id) +'_2020'
#     team_name_link = teams_df.loc[idx, 'team_name_link']

#     projected_graph(team_id, team_name_link, team_season_id)


def tean_violin(team_id, team_name_link):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    violin_query = """SELECT a.player_name, b.depth_chart_rank, b.season_type, a.value_contributed
                        FROM (SELECT player_name, player_id, SUM(value_contributed) value_contributed
                                FROM all_seasons_value_contributed
                                WHERE team_id = %(team_id)s
                                AND season_end = 2019
                                GROUP BY player_id, player_name
                                ORDER BY value_contributed DESC LIMIT 10) a
                        INNER JOIN all_seasons_discrepancy_depth b
                        ON a.player_id = b.player_id
                        WHERE team_id = %(team_id)s
                        AND season_end = 2019
                        ORDER BY a.value_contributed DESC;"""

    violin_df = pd.read_sql(violin_query, con=conn, params={'team_id': int(team_id)})

    conn.close()
    teams = teams_dict()

    plt.figure(figsize=(8,8))

    try:
        ax = sns.violinplot(x="player_name", y="depth_chart_rank", hue="season_type",
                        data=violin_df, palette={'Regular Season':teams[team_id].get('colors')[1], 'Playoffs':teams[team_id].get('colors')[0]}, split=True)
    except:
        ax = sns.violinplot(x="player_name", y="depth_chart_rank", hue="season_type",
                        data=violin_df, palette={'Regular Season':teams[team_id].get('colors')[1], 'Playoffs':teams[team_id].get('colors')[0]})

    #plt.title(team_name_list[idx], fontsize=18)
    plt.ylabel('Depth Chart Rank', fontsize=14)
    plt.xlabel('')
    plt.ylim([0, None])
    sns.despine(offset=10, trim=True)
    plt.xticks(rotation=15, size=8)
    print('Team Violin: ', team_name_link)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/team_graphs/team_violin/' + team_name_link + '.png'
    plt.savefig(filepath)
    # plt.show()
    plt.close()  

    

for idx in range(len(teams_df)):
    team_id = teams_df.loc[idx, 'team_id'] 
    team_name_link = teams_df.loc[idx, 'team_name_link']

    tean_violin(team_id, team_name_link)