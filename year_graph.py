import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from time import sleep
from classes.teamgamelog import TeamGameLog

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()
# SQL Pull
season_sort = """SELECT game_id::integer,
                        team_id,
                        player_id,
                        player_name,
                        SUM(wins_contr) AS WINS
                 FROM reg_season_2013_14
                 WHERE win_loss = 1
                 GROUP BY game_id, player_id, player_name, team_id
                 ORDER BY game_id"""

# Change line 17 for a new year                                    

season_df = pd.read_sql(season_sort, con=conn)

conn.close()


def graph_season(start_game, end_game, df, colors_dict):
    game = start_game
    counter = 0
    #Create cumulative df
    cumulative_df = df[['team_id', 'player_id', 'player_name']]
    cumulative_df = cumulative_df.drop_duplicates(subset='player_id')
    cumulative_df['WINS'] = 0.
    

    while game <= end_game:
        next_row = copy.deepcopy(game)
        while next_row == game:
            cur_player = df.loc[counter]['player_id']
            cur_wins = df.loc[counter]['wins']
            player_index = cumulative_df.index[cumulative_df['player_id'] == cur_player].astype(int)
            cumulative_df.at[player_index, 'WINS'] = cumulative_df.loc[player_index]['WINS'] + cur_wins
            counter += 1
            next_row = df.loc[counter + 1]['game_id']

        # if previous_day != current_day:
        top20 = cumulative_df[['team_id','player_name', 'WINS']].sort_values(by=['WINS'], ascending=False)
        top20 = top20[['team_id','player_name', 'WINS']]
        top20 = top20.iloc[:20, :].sort_values(by=['WINS'])
        teams = top20['team_id'].to_list()
        
        # Assign colors to different portions of graph
        bar_colors = []
        label_colors = []
        outline_colors = []
        for idx, team in enumerate(teams):
            bar_colors.append(colors_dict.get(teams[idx])[1])
            label_colors.append(colors_dict.get(teams[idx])[0])
            outline_colors.append(colors_dict.get(teams[idx])[2])

        # Create top 20
        top20 = top20[['player_name', 'WINS']]
        graph = top20.plot.barh(y='WINS', x='player_name', figsize=(20,15), color=bar_colors, edgecolor=outline_colors, linewidth=1.5)
        
        # Plot Top 20
        plt.title('GAME: {}'.format(str(game)[-4:]))
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=10)
        for xtick, color in zip(graph.get_yticklabels(), label_colors):
            xtick.set_color(color)
        if df.loc[counter + 1]['game_id'] == end_game:
            plt.show(block=False)
            plt.pause(60)
            plt.close()
            break
        plt.show(block=False)
        plt.pause(.0001)
        plt.close()
        game = df.loc[counter + 1]['game_id']

# Team colors for matplot lib
team_colors = {1610612737:['#E03A3E', '#26282A', '#C1D32F'],
               1610612738:['#000000', '#007A33', '#BA9653'],
               1610612751:['#000000', '#FFFFFF', '#000000'],
               1610612766:['#1D1160', '#00788C', '#A1A1A4'],
               1610612741:['#000000', '#CE1141','#000000'],
               1610612739:['#6F263D', '#000000', '#FFB81C'],
               1610612742:['#00538C', '#B8C4CA', '#002B5E', '#000000'],
               1610612743:['#8B2131', '#0E2240','#FEC524', '#1D428A'],
               1610612765:['#C8102E', '#006BB6', '#BEC0C2', '#002D62'],
               1610612744:['#26282A', '#006BB6', '#FDB927'],
               1610612745:['#000000', '#CE1141', '#C4CED4'],
               1610612754:['#BEC0C2', '#FDBB30', '#002D62'],
               1610612746:['#000000', '#C8102E', '#1D42BA', '#BEC0C2'],
               1610612747:['#000000', '#552583','#FDB927'],
               1610612763:['#707271', '#5D76A9', '#12173F', '#F5B112'],
               1610612748:['#000000', '#98002E', '#F9A01B'],
               1610612749:['#000000', '#EEE1C6', '#00471B'],
               1610612750:['#236192', '#0C2340', '#78BE20', '#9EA2A2'],
               1610612740:['#85714D', '#0C2340', '#C8102E'],
               1610612752:['#BEC0C2', '#006BB6', '#F58426'],
               1610612760:['#002D62', '#007AC1', '#EF3B24', '#FDBB30'],
               1610612753:['#000000', '#0077C0', '#C4CED4'],
               1610612755:['#C4CED4', '#006BB6', '#ED174C', '#002B5C'],
               1610612756:['#000000', '#1D1160', '#E56020', '#63727A', '#F9AD1B'],
               1610612757:['#000000', '#E03A3E', '#000000'],
               1610612758:['#000000', '#5A2D81', '#63727A'],
               1610612759:['#000000', '#C4CED4', '#000000'],
               1610612761:['#A1A1A4', '#000000', '#CE1141'],
               1610612762:['#F9A01B', '#002B5C', '#00471B'],
               1610612764:[ '#E31837', '#FFFFFF', '#002B5C']}

graph_season(21300001, 21301231, season_df, team_colors)