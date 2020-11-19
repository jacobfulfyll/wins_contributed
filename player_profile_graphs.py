import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
import random
import numpy as np

#import matplotlib.font_manager
#print(matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'))

def nth_repl(s, sub, repl, nth):
    find = s.find(sub)
    # if find is not p1 we have found at least one match for the substring
    i = find != -1
    # loop util we find the nth or we find no match
    while find != -1 and i != nth:
        # find + 1 means we start at the last match start index + 1
        find = s.find(sub, find + 1)
        i += 1
    # if i  is equal to nth we found nth matches so replace
    if i == nth:
        return s[:find]+repl+s[find + len(sub):]
    return s

def player_timeline():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    # SQL Pull
    unique_players = """SELECT DISTINCT player_id, player_name
                        FROM all_games_ranked"""

    players_df = pd.read_sql(unique_players, con=conn)
    player_id_list = players_df['player_id'].values.tolist()
    player_name_list = players_df['player_name'].values.tolist()

    for idx, player_id in enumerate(player_id_list):

        reg_season = """SELECT game_id, player_id, player_name, wins_contr, win_loss
                                        FROM all_games_ranked
                                        WHERE season_type = 'Regular Season'
                                        AND player_id = %(player_id)s
                                        ORDER BY game_id"""
            
        playoffs = """SELECT game_id, player_id, player_name, wins_contr, win_loss
                                        FROM all_games_ranked
                                        WHERE season_type = 'Playoffs'
                                        AND player_id = %(player_id)s
                                        ORDER BY game_id"""

        reg_season_df = pd.read_sql(reg_season, con=conn, params={'player_id': player_id})
        playoffs_df = pd.read_sql(playoffs, con=conn, params={'player_id': player_id})

        playoffs_df['game_id'] = [x.replace('4', '2', 1) for x in playoffs_df['game_id'].tolist()]
        playoffs_df['game_id'] = [nth_repl(s, "0","5",3) for s in playoffs_df['game_id'].tolist()]
        playoffs_df['game_id'] = [nth_repl(s, "0","5",3) for s in playoffs_df['game_id'].tolist()]
        playoffs_df['game_id'] = [int(x) for x in playoffs_df['game_id'].tolist()]
        reg_season_df['game_id'] = [int(x) for x in reg_season_df['game_id'].tolist()]

        all_games_df = reg_season_df.append(playoffs_df)

        loss_df = all_games_df[all_games_df['win_loss'] == 0].sort_values('game_id')
        wins_df = all_games_df[all_games_df['win_loss'] == 1].sort_values('game_id')
        loss_df['Outcome'] = 'Loss'
        wins_df['Outcome'] = 'Win'

        loss_df['cumsum'] = loss_df['wins_contr'].cumsum()
        wins_df['cumsum'] = wins_df['wins_contr'].cumsum()

        all_games_df = loss_df.append(wins_df)
        all_games_df = all_games_df.sort_values('game_id').reset_index(drop=True).reset_index()

        try:
            # sns.set()
            sns.set_style("ticks")
            
            sns.lineplot(x='index', y='cumsum', hue='Outcome', data=all_games_df, palette={'Loss':'#4b86b4', 'Win':'#ffab00'}, hue_order=['Win', 'Loss'])
        except:
            pass

        plt.legend(title='Outcome', labels=['Win', 'Loss'])
        #plt.title(player_name_list[idx], fontsize=18)
        plt.ylabel('Total Contributed', fontsize=10)
        plt.xlabel('Games Played',fontsize=10)

        save_name = player_name_list[idx].replace(' ', '_').replace("'", "").replace('.','').lower()
        print('Player Timeline: ', save_name)        
        filepath = '/Users/jacobpress/Desktop/website_s3/value_contr/player_graphs/player_timeline/' + save_name
        sns.despine(offset=10, trim=True)
        plt.savefig(filepath)
        
        #plt.show
        plt.close()
        
    conn.close()

def player_distribution():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    # SQL Pull
    unique_players = """SELECT DISTINCT player_id, player_name
                        FROM all_games_ranked"""

    players_df = pd.read_sql(unique_players, con=conn)
    player_id_list = players_df['player_id'].values.tolist()
    player_name_list = players_df['player_name'].values.tolist()

    for idx, player_id in enumerate(player_id_list):

        reg_season_wins_by_game = """SELECT player_id, player_name, wins_contr
                                        FROM all_games_ranked
                                        WHERE season_type = 'Regular Season'
                                        AND win_loss = 1
                                        AND player_id = %(player_id)s
                                        ORDER BY game_id"""
            
        reg_season_losses_by_game = """SELECT player_id, player_name, wins_contr
                                        FROM all_games_ranked
                                        WHERE win_loss = 0
                                        AND season_type = 'Regular Season'
                                        AND player_id = %(player_id)s"""

        playoffs_wins_by_game = """SELECT player_id, player_name, wins_contr
                                        FROM all_games_ranked
                                        WHERE win_loss = 1
                                        AND season_type = 'Playoffs'
                                        AND player_id = %(player_id)s"""
            
        playoffs_losses_by_game = """SELECT player_id, player_name, wins_contr
                                        FROM all_games_ranked
                                        WHERE win_loss = 0
                                        AND season_type = 'Playoffs'
                                        AND player_id = %(player_id)s"""

        reg_season_wins_df = pd.read_sql(reg_season_wins_by_game, con=conn, params={'player_id': player_id})
        reg_season_losses_df = pd.read_sql(reg_season_losses_by_game, con=conn, params={'player_id': player_id})
        playoffs_wins_df = pd.read_sql(playoffs_wins_by_game, con=conn, params={'player_id': player_id})
        playoffs_losses_df = pd.read_sql(playoffs_losses_by_game, con=conn, params={'player_id': player_id})
        

        # sns.set()
        sns.set_style("ticks")
        try:
            sns.distplot(reg_season_wins_df['wins_contr'], rug=True, hist=False, label='Reg Season Wins', kde_kws={"color":'#ffab00'}, rug_kws={"color":'#ffab00'})
        except:
            pass
        try:
            sns.distplot(reg_season_losses_df['wins_contr'], rug=True, hist=False, label='Reg Season Losses', kde_kws={"color":'#4b86b4'}, rug_kws={"color":'#4b86b4'})
        except:
            pass
        try:
            sns.distplot(playoffs_wins_df['wins_contr'], rug=True, hist=False, label='Playoff Wins', kde_kws={"color":'#47813E'}, rug_kws={"color":'#47813E'}) 
        except:
            pass
        try:
            sns.distplot(playoffs_losses_df['wins_contr'], rug=True, hist=False, label='Playoff Losses', kde_kws={"color":'#8D605A'}, rug_kws={"color":'#8D605A'})
        except: pass


        plt.xlim(0, None)
        #plt.title(player_name_list[idx], fontsize=18)
        plt.ylabel('Density', fontsize=10)
        plt.xlabel('Game Contribution',fontsize=10)
        sns.despine(offset=10, trim=True)

        save_name = player_name_list[idx].replace(' ', '_').replace("'", "").replace('.','').lower()
        print('Player Distribution: ', save_name)             
        filepath = '/Users/jacobpress/Desktop/website_s3/value_contr/player_graphs/player_distribution/' + save_name
        plt.savefig(filepath)

        #plt.show()
        plt.close()
        
    conn.close()

def player_seasons():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    # SQL Pull
    unique_players = """SELECT DISTINCT player_id, player_name
                        FROM all_games_ranked"""

    players_df = pd.read_sql(unique_players, con=conn)
    player_id_list = players_df['player_id'].values.tolist()
    player_name_list = players_df['player_name'].values.tolist()
    
    check = 0
    for idx, player_id in enumerate(player_id_list):

        try:
            by_season = """SELECT season_end, player_id, player_name, wins_contr, wins_contr_in_loss
                                FROM yearly_stats_by_season
                                WHERE season_type = 'Regular Season'
                                AND player_id = %(player_id)s
                                ORDER BY season_end"""

            by_season_df = pd.read_sql(by_season, con=conn, params={'player_id': player_id})
            wins_contr = by_season_df[['season_end', 'player_id', 'player_name', 'wins_contr']]
            losses_contr = by_season_df[['season_end', 'player_id', 'player_name', 'wins_contr_in_loss']]
            losses_contr = losses_contr.rename(columns={"wins_contr_in_loss": "wins_contr"})
            wins_contr['Outcome'] = 'Win'
            losses_contr['Outcome'] = 'Loss'
            by_season_df = wins_contr.append(losses_contr)
            
            try:
                prediction = """SELECT player_id, player_name, final_player_wins, final_player_losses
                                    FROM player_projections_2020_updated
                                    WHERE player_id = %(player_id)s"""
                print('hello')
                prediction_df = pd.read_sql(prediction, con=conn, params={'player_id': player_id})
                print(prediction_df)
                prediction_df['season_end'] = 2020
                wins_contr_1 = prediction_df[['season_end', 'player_id', 'player_name', 'final_player_wins']]
                losses_contr_1 = prediction_df[['season_end', 'player_id', 'player_name', 'final_player_losses']]
                losses_contr_1 = losses_contr_1.rename(columns={"final_player_losses": "wins_contr"})
                wins_contr_1 = wins_contr_1.rename(columns={"final_player_wins": "wins_contr"})
                wins_contr_1['Outcome'] = 'Win'
                losses_contr_1['Outcome'] = 'Loss'
                prediction_df = wins_contr_1.append(losses_contr_1)

                by_season_df = by_season_df.append(prediction_df)
                print(by_season_df)

            except:
                pass

            #sns.set()
            sns.set_style("white")
            sns.despine()
            sns.barplot(x="season_end", y="wins_contr", hue='Outcome', data=by_season_df, palette={'Win':'#ffab00', 'Loss':'#4b86b4'}, saturation=.75)
            #plt.title(player_name_list[idx], fontsize=18)
            plt.ylabel('Total Contributed', fontsize=10)
            plt.xlabel('Season End',fontsize=10)
            sns.despine(offset=10, trim=True)

            save_name = player_name_list[idx].strip('.').replace(' ', '_').replace("'", "").replace('.','').lower()
            print('Player Career: ', save_name)              
            filepath = '/Users/jacobpress/Desktop/website_s3/value_contr/player_graphs/player_seasons/' + save_name
            plt.savefig(filepath)
            #plt.show()
            plt.close()
        except:
            pass
        
    conn.close()

#player_seasons()

def create_player_profile_graphs():
    player_timeline()
    player_distribution()
    player_seasons()



create_player_profile_graphs()