import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
import random
import numpy as np
import plotly.graph_objects as go
from time import sleep

conn = pg2.connect(dbname= "personal_website", host = "localhost")
cur = conn.cursor()

players_query = """SELECT player_id, player_name_link
                    FROM nba_players;"""

players_df = pd.read_sql(players_query, con=conn)

conn.close()

def win_loss_contributed_bar(player_id, player_name_link):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    wins_contr_query = """SELECT season_end, SUM(value_contributed) value_contributed, win_loss
                        FROM all_seasons_value_contributed
                        WHERE player_id = %(player_id)s
                        AND win_loss = 1
                        AND season_type = 'Regular Season'
                        GROUP BY season_end, win_loss
                        ORDER BY season_end;"""
    
    losses_contr_query = """SELECT season_end, SUM(value_contributed) value_contributed, win_loss
                        FROM all_seasons_value_contributed
                        WHERE player_id = %(player_id)s
                        AND win_loss = 0
                        AND season_type = 'Regular Season'
                        GROUP BY season_end, win_loss
                        ORDER BY season_end;"""

    wins_contr_df = pd.read_sql(wins_contr_query, con=conn, params={'player_id':int(player_id)})
    losses_contr_df = pd.read_sql(losses_contr_query, con=conn, params={'player_id':int(player_id)})
    conn.close()

    try:
        player_season_id = str(player_id) + '_2020' 
        conn = pg2.connect(dbname= "personal_website", host = "localhost")
        cur = conn.cursor()
        
        prediction_query = """SELECT wins_contr, losses_contr
                                FROM player_predictions
                                WHERE player_season_id = %(player_season_id)s;"""

        prediction_df = pd.read_sql(prediction_query, con=conn, params={'player_season_id':player_season_id})
        prediction_df = prediction_df.reset_index(drop=True)
        conn.close()

        graph_df = wins_contr_df.append(losses_contr_df).reset_index(drop=True)

        graph_df.loc[len(graph_df), :] = [2020, prediction_df.loc[0, 'wins_contr'], 1]
        graph_df.loc[len(graph_df), :] = [2020, prediction_df.loc[0, 'losses_contr'], 0]
    except:
        pass
    
    graph_df['Outcome'] = ['Win' if x == 1 else 'Loss' for x in graph_df['win_loss']]
    graph_df['season_end'] = [int(x) for x in graph_df['season_end']]

    plt.figure(figsize=(8,6))
    
    sns.set_style("white")
    sns.despine()
    sns.barplot(x='season_end', y='value_contributed', hue='Outcome', data=graph_df, palette={'Win':'#ffab00', 'Loss':'#4b86b4'}, saturation=.75)
    #plt.title(player_name_list[idx], fontsize=18)
    plt.ylabel('Total Contributed', fontsize=14)
    plt.xlabel('Season End',fontsize=14)

    sns.despine(offset=10, trim=True)
    

    print('Player Career: ', player_name_link)              
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/player_graphs/regular_season_value/' + player_name_link + '.png'
    plt.savefig(filepath)
    plt.close()


for idx in range(len(players_df)):
    player_id = players_df.loc[idx, 'player_id']
    player_name_link = players_df.loc[idx, 'player_name_link']
    win_loss_contributed_bar(player_id, player_name_link)



def player_distribution(player_id, player_name_link):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()


    reg_season_wins_contr_query = """SELECT value_contributed
                                        FROM all_seasons_value_contributed
                                        WHERE player_id = %(player_id)s
                                        AND win_loss = 1
                                        AND season_type = 'Regular Season';"""
    
    reg_season_losses_contr_query = """SELECT value_contributed
                                        FROM all_seasons_value_contributed
                                        WHERE player_id = %(player_id)s
                                        AND win_loss = 0
                                        AND season_type = 'Regular Season';"""

    playoffs_wins_contr_query = """SELECT value_contributed
                                    FROM all_seasons_value_contributed
                                    WHERE win_loss = 1
                                    AND season_type = 'Playoffs'
                                    AND player_id = %(player_id)s;"""
        
    playoffs_losses_contr_query = """SELECT value_contributed
                                        FROM all_seasons_value_contributed
                                        WHERE win_loss = 0
                                        AND season_type = 'Playoffs'
                                        AND player_id = %(player_id)s;"""

    reg_season_wins_df = pd.read_sql(reg_season_wins_contr_query, con=conn, params={'player_id': int(player_id)})
    reg_season_losses_df = pd.read_sql(reg_season_losses_contr_query, con=conn, params={'player_id': int(player_id)})
    playoffs_wins_df = pd.read_sql(playoffs_wins_contr_query, con=conn, params={'player_id': int(player_id)})
    playoffs_losses_df = pd.read_sql(playoffs_losses_contr_query, con=conn, params={'player_id': int(player_id)})
    
    conn.close()
    plt.figure(figsize=(8,6))
    # sns.set()
    sns.set_style("ticks")
    try:
        sns.distplot(reg_season_wins_df['value_contributed'], rug=True, hist=False, label='Reg Season Wins', kde_kws={"color":'#ffab00'}, rug_kws={"color":'#ffab00'})
    except:
        pass
    try:
        sns.distplot(reg_season_losses_df['value_contributed'], rug=True, hist=False, label='Reg Season Losses', kde_kws={"color":'#4b86b4'}, rug_kws={"color":'#4b86b4'})
    except:
        pass
    try:
        sns.distplot(playoffs_wins_df['value_contributed'], rug=True, hist=False, label='Playoff Wins', kde_kws={"color":'#47813E'}, rug_kws={"color":'#47813E'}) 
    except:
        pass
    try:
        sns.distplot(playoffs_losses_df['value_contributed'], rug=True, hist=False, label='Playoff Losses', kde_kws={"color":'#8D605A'}, rug_kws={"color":'#8D605A'})
    except: pass


    plt.xlim(0, None)
    #plt.title(player_name_list[idx], fontsize=18)
    plt.ylabel('Density', fontsize=14)
    plt.xlabel('Average Contributed',fontsize=14)
    sns.despine(offset=10, trim=True)


    print('Player Distribution: ', player_name_link)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/player_graphs/player_distribution/' + player_name_link + '.png'
    plt.savefig(filepath)

    # plt.show()
    plt.close()

# for idx in range(len(players_df)):
#     player_id = players_df.loc[idx, 'player_id']
#     player_name_link = players_df.loc[idx, 'player_name_link']
#     player_distribution(player_id, player_name_link)  



def player_radar(player_id, player_name_link):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()


    radar_query = """SELECT player_name, season_end, stat_type, pca_score
                                        FROM pca_similarity_components
                                        WHERE player_id = %(player_id)s
                                        ORDER BY season_end, stat_type;"""


    radar_df = pd.read_sql(radar_query, con=conn, params={'player_id': str(player_id)})

    conn.close()

    categories = radar_df['stat_type'].unique()
    fig = go.Figure()

    for idx, season in enumerate(radar_df['season_end'].unique()):
        fig.add_trace(go.Scatterpolar(
            r=radar_df[radar_df['season_end'] == season]['pca_score'].tolist(),
            theta=categories,
            name=season
        ))

        

    fig.update_layout(
    polar=dict(
        angularaxis_tickfont_size = 10,
        radialaxis=dict(
        visible=True,
        range=[-.95, 1.55],
        tickfont_size = 8,
        )),
    legend=go.layout.Legend(
        x=.9,
        y=1.1,
        font=dict(
            family="sans-serif",
            size=10,
            color="black"
        )),
    width=700,
    height=500
    )

    print('Player Radar: ' + player_name_link)
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/player_graphs/player_radar/' + player_name_link + '.svg'

    # fig.show()
    # sleep(10)
    fig.write_image(filepath)


# for idx in range(len(players_df)):
#     player_id = players_df.loc[idx, 'player_id']
#     player_name_link = players_df.loc[idx, 'player_name_link']
#     player_radar(player_id, player_name_link) 


def player_box(player_id, player_name_link):

    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    box_query = """SELECT season_end, value_contributed, season_type
                        FROM all_seasons_value_contributed
                        WHERE player_id = %(player_id)s;"""

    box_df = pd.read_sql(box_query, con=conn, params={'player_id': int(player_id)})

    conn.close()

    plt.figure(figsize=(8,6))

    ax = sns.boxplot(x="season_end", y="value_contributed", hue="season_type",
                        data=box_df, palette="muted")

    #plt.title(player_name_list[idx], fontsize=18)
    plt.ylabel('Value Contributed', fontsize=14)
    plt.xlabel('Season',fontsize=14)
    sns.despine(offset=10, trim=True)
    print('Player Box: ', player_name_link)             
    filepath = '/Users/jacobpress/Desktop/website_s3/val_contr/player_graphs/player_box/' + player_name_link + '.png'
    plt.savefig(filepath)
    plt.close()

# for idx in range(len(players_df)):
#     player_id = players_df.loc[idx, 'player_id']
#     player_name_link = players_df.loc[idx, 'player_name_link']
#     player_box(player_id, player_name_link) 


