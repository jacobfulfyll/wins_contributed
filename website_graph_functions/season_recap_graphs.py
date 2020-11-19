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

def graph_regular_season(season_end):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    reg_season_wins_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val, MAX(value_contributed) "Max Game"
                        FROM all_seasons_value_contributed
                        WHERE season_end = %(season_end)s
                        AND season_type = 'Regular Season'
                        AND win_loss = 1
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    reg_season_losses_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val,  MAX(value_contributed) "Max Game"
                        FROM all_seasons_value_contributed
                        WHERE season_end = %(season_end)s
                        AND season_type = 'Regular Season'
                        AND win_loss = 0
                        GROUP BY player_id, player_name, season_type, win_loss;"""


    reg_season_wins_df = pd.read_sql(reg_season_wins_query, con=conn, params={'season_end': season_end})
    reg_season_losses_df = pd.read_sql(reg_season_losses_query, con=conn, params={'season_end': season_end})
    conn.close()
    

    # fig = plt.figure(figsize=(800/192, 800/192), dpi=192)
    fig, (ax1, ax2) = plt.subplots(2, figsize=(567/192, 500/192), dpi=192, sharex=True)

    sns.scatterplot(x="avg_val", y="total_val", data=reg_season_wins_df , hue='Max Game', alpha=.5, ax=ax1, s=4, linewidth=0)
    sns.scatterplot(x="avg_val", y="total_val", data=reg_season_losses_df, hue='Max Game', alpha=.5, ax=ax2, s=4, linewidth=0)
    
    # ax1.set_xticklabels({'fontsize':'10px'})
    plt.xlabel('Value Contributed (Per Game)', fontsize=6)
    ax1.set_ylabel('Wins', fontsize=4)
    ax2.set_ylabel('Losses', fontsize=4)

    ax1.tick_params(axis='both',labelsize=4, length=2, width=.5)
    ax2.tick_params(axis='both',labelsize=4, length=2, width=.5)

    # Create the figure
    ax1.legend(loc=2, fontsize=.2, markerscale=.2, prop={'size': 3})
    ax2.get_legend().remove()



    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # handles, labels = ax1.get_legend_handles_labels()
    # ax1.legend(handles, labels, loc=2, )


    df_list = [reg_season_wins_df, reg_season_losses_df]
    ax_list = [ax1, ax2]
    for i, ax in enumerate(ax_list):
        #print(sample_size)
        #sleep(2)
        y_max = ax.get_ylim()[1]
        y_min = ax.get_ylim()[0]
        x_max = ax.get_xlim()[1]
        x_min = ax.get_xlim()[0]
        
        character_width = 0.015903216584521756 * (x_max - x_min)
        character_height = 0.029 * (y_max - y_min)  

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


    print('Regular Season: ', season_end)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/league_graphs/regular_season/' + str(season_end) + '.png'
    plt.savefig(filepath)

    # plt.show()
    plt.close()

# for season in range(6):
#     graph_regular_season(2014 + season)


def graph_playoffs(season_end):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    playoffs_wins_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val, MAX(value_contributed) "Max Game"
                        FROM all_seasons_value_contributed
                        WHERE season_end = %(season_end)s
                        AND season_type = 'Playoffs'
                        AND win_loss = 1
                        GROUP BY player_id, player_name, season_type, win_loss;"""

    playoffs_losses_query = """SELECT player_name, season_type, win_loss, AVG(value_contributed) avg_val, SUM(value_contributed) total_val,  MAX(value_contributed) "Max Game"
                        FROM all_seasons_value_contributed
                        WHERE season_end = %(season_end)s
                        AND season_type = 'Playoffs'
                        AND win_loss = 0
                        GROUP BY player_id, player_name, season_type, win_loss;"""


    playoffs_wins_df = pd.read_sql(playoffs_wins_query, con=conn, params={'season_end': season_end})
    playoffs_losses_df = pd.read_sql(playoffs_losses_query, con=conn, params={'season_end': season_end})
    conn.close()
    

    # fig = plt.figure(figsize=(800/192, 800/192), dpi=192)
    fig, (ax1, ax2) = plt.subplots(2, figsize=(567/192, 500/192), dpi=192, sharex=True)

    sns.scatterplot(x="avg_val", y="total_val", data=playoffs_wins_df , hue='Max Game', alpha=.5, ax=ax1, s=4, linewidth=0)
    sns.scatterplot(x="avg_val", y="total_val", data=playoffs_losses_df, hue='Max Game', alpha=.5, ax=ax2, s=4, linewidth=0)
    
    # ax1.set_xticklabels({'fontsize':'10px'})
    plt.xlabel('Value Contributed (Per Game)', fontsize=6)
    ax1.set_ylabel('Wins', fontsize=4)
    ax2.set_ylabel('Losses', fontsize=4)

    ax1.tick_params(axis='both',labelsize=4, length=2, width=.5)
    ax2.tick_params(axis='both',labelsize=4, length=2, width=.5)

    # Create the figure
    ax1.legend(loc=2, fontsize=.2, markerscale=.2, prop={'size': 3})
    ax2.get_legend().remove()



    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # handles, labels = ax1.get_legend_handles_labels()
    # ax1.legend(handles, labels, loc=2, )


    df_list = [playoffs_wins_df, playoffs_losses_df]
    ax_list = [ax1, ax2]
    for i, ax in enumerate(ax_list):
        #print(sample_size)
        #sleep(2)
        y_max = ax.get_ylim()[1]
        y_min = ax.get_ylim()[0]
        x_max = ax.get_xlim()[1]
        x_min = ax.get_xlim()[0]
        
        character_width = 0.015903216584521756 * (x_max - x_min)
        character_height = 0.029 * (y_max - y_min)  

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


    print('Playoffs: ', season_end)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/league_graphs/playoffs/' + str(season_end) + '.png'
    plt.savefig(filepath)

    # plt.show()
    plt.close()

# for season in range(6):
#     graph_playoffs(2014 + season)

def graph_mvp_race(season_end):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    # mvp_query = """SELECT b.game_id, b.player_name, b.value_contributed, b.team_id
    #                 FROM (SELECT player_id, SUM(value_contributed) value_contributed
    #                         FROM all_seasons_value_contributed
    #                         WHERE season_end = %(season_end)s
    #                         AND season_type = 'Regular Season'
    #                         AND win_loss = 1
    #                         GROUP BY player_id
    #                         ORDER BY value_contributed DESC LIMIT 20) a
    #                 INNER JOIN all_seasons_value_contributed b
    #                 ON a.player_id = b.player_id
    #                 WHERE season_end = %(season_end)s
    #                 AND season_type ='Regular Season'
    #                 AND win_loss = 1;"""

    # mvp_query = """SELECT b.game_id,
    #                     b.team_id,
    #                     b.player_name,
    #                     b.value_contributed
    #             FROM (SELECT player_id, SUM(value_contributed) value_contributed
    #                          FROM value_contributed_2019_20
    #                          WHERE win_loss = 1
    #                          GROUP BY player_id
    #                          ORDER BY value_contributed DESC LIMIT 40) a
    #              INNER JOIN value_contributed_2019_20 b
    #              ON a.player_id = b.player_id
    #              WHERE win_loss = 1
    #              ORDER BY game_id;"""

    mvp_df = pd.read_sql(mvp_query, con=conn, params={'season_end': season_end})

    conn.close()

    race_df = pd.DataFrame()
    for player in mvp_df['player_name'].unique():
        append_df = mvp_df[mvp_df['player_name'] == player].reset_index(drop=True)
        cum_list = []
        current_score = 0
        for idx in range(len(append_df)):
            current_score += append_df.loc[idx, 'value_contributed']
            cum_list.append(current_score)

        append_df['cum_value'] = cum_list

        race_df = race_df.append(append_df)
    race_df['game'] = [int(x[-4:]) for x in race_df['game_id']]
    print(race_df)
    plt.figure(figsize=(8,6))
    race_df = race_df.sort_values('cum_value', ascending=False)

    ax = sns.lineplot(x="game", y="cum_value", hue="player_name", data=race_df, legend='brief')
    teams = teams_dict()

    players = race_df.sort_values('cum_value', ascending=False)['player_name'].unique()
    teams_list = []
    legend_elements = []
    line_style = ['-', '--', '-.', ':']
    for idx, player in enumerate(players):
        team_id = race_df[race_df['player_name'] ==  player].reset_index(drop=True).loc[0, 'team_id']
        teams_list.append(team_id)
        legend_elements.append(Line2D([0],[0],label=player, color=teams[team_id].get('colors')[idx % 2], linestyle=line_style[idx % 4], alpha=1 - (.03*idx)))


    print(len(teams_list))
    print(ax.lines)
    for idx in range(len(ax.lines)):
        ax.lines[idx].set_linestyle(line_style[idx % 4])
        ax.lines[idx].set_color(teams[teams_list[idx % 20]].get('colors')[idx % 2])
        ax.lines[idx].set_alpha(1 - (.03*idx))
        
        

    # Create the figure
    ax.legend(handles=legend_elements, loc=2, prop={'size': 6})
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xlabel('Game', fontsize=10)
    ax.set_ylabel('Wins Contributed', fontsize=10)
    ax.tick_params(axis='both',labelsize=7, length=2, width=1)

    print('MVP Race: ', season_end)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/league_graphs/mvp_race/' + str(season_end) + '.png'
    # plt.savefig(filepath)

    plt.show()
    plt.close()

# for season in range(6):
#     graph_mvp_race(2014 + season)

# graph_mvp_race(2020)

def graph_dpy(season_end):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    defense_query = """SELECT player_id, player_name, SUM(dreb_blk) dreb_blk, SUM(dreb_no_blk) dreb_no_blk, SUM(stls_score) stls_score, SUM(blks_score) blks_score, SUM(dfg_score) dfg_score, SUM(positive_def_fouls) positive_def_fouls, SUM(negative_def_fouls) negative_def_fouls, SUM(total_value) total_value, SUM(value_contributed) value_contributed
                        FROM all_seasons_value_contributed
                        WHERE season_end = %(season_end)s
                        AND season_type = 'Regular Season'
                        AND win_loss = 1
                        GROUP BY player_id, player_name;"""

select ROW_NUMBER() OVER (ORDER BY a.avg_val DESC) AS No, a.player_id, a.player_name, a.avg_val from(select player_id, player_name, SUM(value_contributed) avg_val from value_contributed_2019_20 where win_loss = 1 group by player_name, player_id order by avg_val desc) a;

    defense_df = pd.read_sql(defense_query, con=conn, params={'season_end': season_end})

    conn.close()

    defense_df['def_total_val'] = defense_df.loc[:,'dreb_blk':'negative_def_fouls'].sum(axis = 1)
    defense_df['def_val_contr'] = defense_df['def_total_val'] / defense_df['total_value'] * defense_df['value_contributed']
    defense_df['foul_value'] = defense_df['positive_def_fouls'] + defense_df['negative_def_fouls']

    defense_df = defense_df[defense_df['value_contributed'] > defense_df['def_val_contr']].sort_values('def_val_contr', ascending=False).reset_index(drop=True).loc[0:20, :]
    print(defense_df)
    col_list = ['dreb_no_blk', 'stls_score', 'blks_score', 'dfg_score', 'foul_value']
    for col in col_list:
        defense_df[col] = (defense_df[col] / defense_df['def_total_val']) * defense_df['def_val_contr']

    plt.figure(figsize=(8,6))

    ax = plt.subplot(111)
    width=.9

    p1 = ax.bar(defense_df['player_name'], defense_df['dreb_no_blk'], width, color=(0.0549, 0.6549, 0.7098, 0.6))
    p2 = ax.bar(defense_df['player_name'], defense_df['stls_score'], width, bottom=defense_df['dreb_no_blk'], color=(0.0471, 0.2902, 0.3765, 0.6))
    p3 = ax.bar(defense_df['player_name'], defense_df['blks_score'], width, 
                bottom=np.array(defense_df['dreb_no_blk'])+np.array(defense_df['stls_score']), color=(0.9373, 0.4235, 0.2, 0.6))
    p4 = ax.bar(defense_df['player_name'], defense_df['dfg_score'], width,
                bottom=np.array(defense_df['dreb_no_blk'])+np.array(defense_df['stls_score'])+np.array(defense_df['blks_score']),
                color=(0.6706, 0.8745, 0.9450, 0.6))
    p5 = ax.bar(defense_df['player_name'], defense_df['foul_value'], width,
                bottom=np.array(defense_df['dreb_no_blk'])+np.array(defense_df['stls_score'])+np.array(defense_df['blks_score'])+np.array(defense_df['dfg_score']),
                color=(0.8824, 0.8667, 0.8588, 1))

    # ax = sns.barplot(x="player_name", y="def_val_contr", data=defense_df)

    # ax.legend(handles=legend_elements, loc=2, prop={'size': 6})
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_ylabel('Defensive Value', fontsize=10)
    ax.set_xlabel('')
    ax.tick_params(axis='both',labelsize=7, length=2, width=1)
    plt.xticks(rotation=30, size=5, ha="right")
    Stat = ['Defensive Rebounds', 'Steals', 'Blocks', 'Defended Field Goals', 'Fouls']
    plt.legend(Stat,loc=1)
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/league_graphs/dpy/' + str(season_end) + '.png'
    plt.savefig(filepath)
    # plt.show()
    plt.close()

# for season in range(6):
#     graph_dpy(2014 + season)