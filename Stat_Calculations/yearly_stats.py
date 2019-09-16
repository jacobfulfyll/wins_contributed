import pandas as pd
from Stat_Calculations.compile_data import create_stats_df
import numpy as np
import psycopg2 as pg2
from sqlalchemy import create_engine

master_df = create_stats_df()
#print(master_df)

def yearly_games_played(): 
    wins_df = master_df[(master_df['jacob_value'] != 0) & (master_df['win_loss'] == 1)][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    wins_df = wins_df.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    wins_df = wins_df.count()
    wins_df = wins_df.rename(columns={"wins_contr": "wins"})

    losses_df = master_df[(master_df['jacob_value'] != 0) & (master_df['win_loss'] == 0)][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    losses_df = losses_df.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    losses_df = losses_df.count()
    losses_df = losses_df.rename(columns={"wins_contr": "losses"})

    yearly_df = wins_df.merge(losses_df, on=['season_type', 'season_end', 'player_id', 'player_name'])
    yearly_df['games_played'] = yearly_df['wins'] + yearly_df['losses']

    return yearly_df

def wins_contributed_basics():
    yearly_df = master_df[master_df['win_loss'] == 1][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df = yearly_df.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df = yearly_df.aggregate(np.sum)
    
    yearly_df = yearly_df.merge(yearly_games_played(), on=['season_type', 'season_end', 'player_id', 'player_name'])
    yearly_df['avg_wc'] = yearly_df['wins_contr'] / yearly_df['wins']

    yearly_df_max = master_df[master_df['win_loss'] == 1][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df_max = yearly_df_max.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df_max = yearly_df_max.aggregate(np.max)
    yearly_df_max = yearly_df_max.rename(columns={"wins_contr": "max_wc"})
    yearly_df = yearly_df.merge(yearly_df_max, on=['season_type', 'season_end', 'player_id', 'player_name'])

    return yearly_df.drop(columns=['wins', 'games_played', 'losses'])

def wins_contributed_in_loss_basics():
    yearly_df = master_df[master_df['win_loss'] == 0][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df = yearly_df.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df = yearly_df.aggregate(np.sum)
    yearly_df = yearly_df.rename(columns={"wins_contr": "wins_contr_in_loss"})

    yearly_df = yearly_df.merge(yearly_games_played(), on=['season_type', 'season_end', 'player_id', 'player_name'])
    yearly_df['avg_wc_il'] = yearly_df['wins_contr_in_loss'] / yearly_df['losses']

    yearly_df_max = master_df[master_df['win_loss'] == 0][['season_type', 'season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df_max = yearly_df_max.groupby(['season_type', 'season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df_max = yearly_df_max.aggregate(np.max)
    yearly_df_max = yearly_df_max.rename(columns={"wins_contr": "max_wc_il"})
    yearly_df = yearly_df.merge(yearly_df_max, on=['season_type', 'season_end', 'player_id', 'player_name'])

    return yearly_df.drop(columns=['wins', 'games_played', 'losses'])


def wc_totals():
    yearly_df = master_df[master_df['win_loss'] == 1][['season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df = yearly_df.groupby(['season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df = yearly_df.aggregate(np.sum)
    
    yearly_df = yearly_df.merge(yearly_games_played(), on=['season_end', 'player_id', 'player_name'])
    yearly_df['avg_wc'] = yearly_df['wins_contr'] / yearly_df['games_played']

    yearly_df_max = master_df[master_df['win_loss'] == 1][['season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df_max = yearly_df_max.groupby(['season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df_max = yearly_df_max.aggregate(np.max)
    yearly_df_max = yearly_df_max.rename(columns={"wins_contr": "max_wc"})
    yearly_df = yearly_df.merge(yearly_df_max, on=['season_end', 'player_id', 'player_name'])
    yearly_df['season_type'] = 'Totals'
    
    return yearly_df.drop(columns=['wins', 'games_played', 'losses'])

def wc_il_totals():
    yearly_df = master_df[master_df['win_loss'] == 0][['season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df = yearly_df.groupby(['season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df = yearly_df.aggregate(np.sum)
    yearly_df = yearly_df.rename(columns={"wins_contr": "wins_contr_in_loss"})

    yearly_df = yearly_df.merge(yearly_games_played(), on=['season_end', 'player_id', 'player_name'])
    yearly_df['avg_wc_il'] = yearly_df['wins_contr_in_loss'] / yearly_df['losses']

    yearly_df_max = master_df[master_df['win_loss'] == 0][['season_end', 'player_id', 'player_name', 'wins_contr']]
    yearly_df_max = yearly_df_max.groupby(['season_end', 'player_id', 'player_name'], as_index=False)
    yearly_df_max = yearly_df_max.aggregate(np.max)
    yearly_df_max = yearly_df_max.rename(columns={"wins_contr": "max_wc_il"})
    yearly_df = yearly_df.merge(yearly_df_max, on=['season_end', 'player_id', 'player_name'])
    yearly_df['season_type'] = 'Totals'


    return yearly_df.drop(columns=['wins', 'games_played', 'losses'])



def wc_lc_yearly_ratio(df):
    df['wc_lc_ratio'] = df['wins_contr'] / df['wins_contr_in_loss']
    #df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['wc_lc_ratio'], how="all")
    #df = df[df['wins_contr'] > 1]
    #print(df.sort_values(by='wc_lc_ratio', ascending=False))

    return df


def fix_traded_players(df):
    traded_players_df = pd.DataFrame(columns=['season_end', 'season_type', 'team_id', 'player_id', 'player_name', 'wins_contr'])
    df = df[df.duplicated(['season_end', 'season_type', 'player_id'], keep=False) == True].sort_values(['player_id', 'season_end', 'season_type', 'wins_contr'], ascending=False)
    df = df.reset_index(drop=True)
    wc = 0
    traded_df_counter = 0

    for idx, row in df.iterrows():
        if idx == 0:
            wc += row['wins_contr']
            team_id = row['team_id']

        elif df.loc[idx - 1, 'season_end'] == df.loc[idx, 'season_end'] and df.loc[idx - 1, 'season_type'] == df.loc[idx, 'season_type'] and df.loc[idx - 1, 'player_id'] == df.loc[idx, 'player_id']:
            wc += row['wins_contr']

        else:
            traded_players_df.loc[traded_df_counter, 'season_end'] = df.loc[idx - 1, 'season_end']
            traded_players_df.loc[traded_df_counter, 'season_type'] = df.loc[idx - 1, 'season_type']
            traded_players_df.loc[traded_df_counter, 'team_id'] = team_id
            traded_players_df.loc[traded_df_counter, 'player_id'] = df.loc[idx - 1, 'player_id']
            traded_players_df.loc[traded_df_counter, 'player_name'] = df.loc[idx - 1, 'player_name']
            traded_players_df.loc[traded_df_counter, 'wins_contr'] = wc
            traded_df_counter += 1
            wc = row['wins_contr']
            team_id = row['team_id']

    return traded_players_df
    

def depth_chart_position_by_year_splits(win_loss=1):
    if win_loss == 'both':
        yearly_df = master_df[['season_type', 'season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]    
    else:
        yearly_df = master_df[master_df['win_loss'] == win_loss][['season_type', 'season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]
    
    yearly_df = yearly_df.groupby(['season_end', 'season_type', 'team_id', 'player_id', 'player_name'], as_index=False)  
    yearly_df = yearly_df.aggregate(np.sum).sort_values(['season_end', 'season_type', 'team_id', 'wins_contr'], ascending=False)

    if win_loss == 0 or win_loss == 'both':
        wins_df = master_df[master_df['win_loss'] == 1][['season_type', 'season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]
        wins_df = wins_df.groupby(['season_end', 'season_type', 'team_id', 'player_id', 'player_name'], as_index=False)  
        wins_df = wins_df.aggregate(np.sum).sort_values(['season_end', 'season_type', 'team_id', 'wins_contr'], ascending=False)
        wins_df = fix_traded_players(wins_df)
        wins_df['win_loss'] = 0

        # print('wins_df #2')
        # print(wins_df[wins_df['player_id'] == 202355])

        traded_players_df = fix_traded_players(yearly_df)

        traded_players_df['win_loss'] = 1
        traded_players_df = traded_players_df.append(wins_df).sort_values(['player_id', 'season_end', 'win_loss'])
        traded_players_df = traded_players_df.reset_index(drop=True)
 
        previous_team_id = None
        for idx, team_id in traded_players_df['team_id'].iteritems():
            if idx == 0:
                pass
            elif previous_team_id == team_id:
                pass
            elif traded_players_df.loc[idx - 1, 'season_end'] == traded_players_df.loc[idx, 'season_end'] and traded_players_df.loc[idx - 1, 'player_id'] == traded_players_df.loc[idx, 'player_id'] and traded_players_df.loc[idx - 1, 'season_type'] == traded_players_df.loc[idx, 'season_type']:
                traded_players_df.loc[idx, 'team_id'] = traded_players_df.loc[idx - 1, 'team_id']
            else:
                pass
            previous_team_id = team_id
        # print('traded_players_df #2')
        # print(traded_players_df[traded_players_df['player_id'] == 202355])

        traded_players_df = traded_players_df[traded_players_df['win_loss'] == 1].drop(columns='win_loss')

        # print('traded_players_df #2')
        # print(traded_players_df[traded_players_df['player_id'] == 202355])

    else:
        traded_players_df = fix_traded_players(yearly_df)

    # print('yearly_df #2')
    # print(yearly_df[yearly_df['player_id'] == 202355])

    yearly_df = yearly_df.drop_duplicates(['season_end', 'season_type', 'player_id'], keep=False)
    yearly_df = yearly_df.append(traded_players_df)
    
    # print('yearly_df #3')
    # print(yearly_df[yearly_df['player_id'] == 202355])

    yearly_df = yearly_df.sort_values(['season_end', 'season_type', 'team_id', 'wins_contr'], ascending=False)
    yearly_df = yearly_df.reset_index(drop=True)

    yearly_df['wc_rank_team'] = 0
    yearly_df['wc_depth_chart_diff'] = 0
    counter = 1
    for idx, row in yearly_df.iterrows():
        if idx == 0:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr'] 
        
        elif idx == len(yearly_df) - 1:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = 0

        elif yearly_df.loc[idx - 1, 'season_end'] == yearly_df.loc[idx, 'season_end'] and yearly_df.loc[idx - 1, 'season_type'] == yearly_df.loc[idx, 'season_type'] and yearly_df.loc[idx - 1, 'team_id'] == yearly_df.loc[idx, 'team_id']:
            
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']
        
        else:
            counter = 1
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx - 1, 'wc_depth_chart_diff'] = 0
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']

    # print('yearly_df #4')
    # print(yearly_df[yearly_df['player_id'] == 202355])

    if win_loss == 0:
        yearly_df = yearly_df.rename(columns={"wins_contr": "wins_contr_in_loss"})
        yearly_df = yearly_df.rename(columns={"wc_rank_team": "wc_il_rank_team"})
        yearly_df = yearly_df.rename(columns={"wc_depth_chart_diff": "wc_il_depth_chart_diff"})
        
        return yearly_df
    
    elif win_loss == 'both':
        yearly_df = yearly_df.rename(columns={"wins_contr": "total_contr"})
        yearly_df = yearly_df.rename(columns={"wc_rank_team": "tc_rank_team"})
        yearly_df = yearly_df.rename(columns={"wc_depth_chart_diff": "tc_depth_chart_diff"})
        
        return yearly_df

    else:
        return yearly_df

#depth_chart_position_by_year_splits(win_loss=0)

def depth_chart_position_by_year_total(win_loss=1):
    if win_loss == 'both':
        yearly_df = master_df[['season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]    
    else:
        yearly_df = master_df[master_df['win_loss'] == win_loss][['season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]
    
    yearly_df = yearly_df.groupby(['season_end', 'team_id', 'player_id', 'player_name'], as_index=False)  
    yearly_df = yearly_df.aggregate(np.sum).sort_values(['season_end', 'team_id', 'wins_contr'], ascending=False)
    yearly_df['season_type'] = 'Total'

    if win_loss == 0 or win_loss == 'both':
        wins_df = master_df[master_df['win_loss'] == 1][['season_type', 'season_end', 'team_id', 'player_id', 'player_name', 'wins_contr']]
        wins_df['season_type'] == 'Total'
        wins_df = wins_df.groupby(['season_end', 'season_type', 'team_id', 'player_id', 'player_name'], as_index=False)  
        wins_df = wins_df.aggregate(np.sum).sort_values(['season_end', 'season_type', 'team_id', 'wins_contr'], ascending=False)
        wins_df = fix_traded_players(wins_df)
        wins_df['win_loss'] = 0

        traded_players_df = fix_traded_players(yearly_df)
        traded_players_df['win_loss'] = 1
        traded_players_df = traded_players_df.append(wins_df).sort_values(['player_id', 'season_end', 'win_loss'])
        traded_players_df = traded_players_df.reset_index(drop=True)

        previous_team_id = None
        for idx, team_id in traded_players_df['team_id'].iteritems():
            if idx == 0:
                pass
            elif previous_team_id == team_id:
                pass
            elif traded_players_df.loc[idx - 1, 'season_end'] == traded_players_df.loc[idx, 'season_end'] and traded_players_df.loc[idx - 1, 'player_id'] == traded_players_df.loc[idx, 'player_id'] and traded_players_df.loc[idx - 1, 'season_type'] == traded_players_df.loc[idx, 'season_type']:
                traded_players_df.loc[idx, 'team_id'] = traded_players_df.loc[idx - 1, 'team_id']
            else:
                pass
            previous_team_id = team_id

        traded_players_df = traded_players_df[traded_players_df['win_loss'] == 1].drop(columns='win_loss')

    else:
        traded_players_df = fix_traded_players(yearly_df)

    yearly_df = yearly_df.drop_duplicates(['season_end', 'player_id'], keep=False)
    yearly_df = yearly_df.append(traded_players_df)
    
    yearly_df = yearly_df.sort_values(['season_end', 'team_id', 'wins_contr'], ascending=False)
    yearly_df = yearly_df.reset_index(drop=True)

    yearly_df['wc_rank_team'] = 0
    yearly_df['wc_depth_chart_diff'] = 0
    counter = 1
    for idx, row in yearly_df.iterrows():
        if idx == 0:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr'] 
        
        elif idx == len(yearly_df) - 1:
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = 0

        elif yearly_df.loc[idx - 1, 'season_end'] == yearly_df.loc[idx, 'season_end'] and yearly_df.loc[idx - 1, 'team_id'] == yearly_df.loc[idx, 'team_id']:
            
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']
        
        else:
            counter = 1
            yearly_df.loc[idx, 'wc_rank_team'] = counter
            counter += 1
            yearly_df.loc[idx - 1, 'wc_depth_chart_diff'] = 0
            yearly_df.loc[idx, 'wc_depth_chart_diff'] = yearly_df.loc[idx, 'wins_contr'] - yearly_df.loc[idx + 1, 'wins_contr']

    if win_loss == 0:
        yearly_df = yearly_df.rename(columns={"wins_contr": "wins_contr_in_loss"})
        yearly_df = yearly_df.rename(columns={"wc_rank_team": "wc_il_rank_team"})
        yearly_df = yearly_df.rename(columns={"wc_depth_chart_diff": "wc_il_depth_chart_diff"})

        return yearly_df
    
    elif win_loss == 'both':
        yearly_df = yearly_df.rename(columns={"wins_contr": "total_contr"})
        yearly_df = yearly_df.rename(columns={"wc_rank_team": "tc_rank_team"})
        yearly_df = yearly_df.rename(columns={"wc_depth_chart_diff": "tc_depth_chart_diff"})

        return yearly_df

    else:
        return yearly_df

#depth_chart_position_by_year_total(win_loss=0)

def season_rankings_by_game(season_end='all', win_loss='both', season_type='total'):
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()
    if season_end != 'all' and win_loss != 'both' and season_type != "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE season_end = %(season_end)s
                        AND win_loss = %(win_loss)s
                        AND season_type = %(season_type)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""
        rankings_df = pd.read_sql(rankings, con=conn, params={'season_end': season_end, 'win_loss': win_loss, 'season_type': season_type})

    
    elif season_end == 'all' and win_loss == 'both' and season_type == "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""
        rankings_df = pd.read_sql(rankings, con=conn)
    
    elif season_end == 'all' and win_loss != 'both' and season_type != "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE win_loss = %(win_loss)s
                        AND season_type = %(season_type)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""

        rankings_df = pd.read_sql(rankings, con=conn, params={'win_loss': win_loss, 'season_type': season_type})


    elif season_end != 'all' and win_loss == 'both' and season_type != "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE season_end = %(season_end)s
                        AND season_type = %(season_type)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""

        rankings_df = pd.read_sql(rankings, con=conn, params={'season_end': season_end, 'season_type': season_type})


    elif season_end != 'all' and win_loss != 'both' and season_type == "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE season_end = %(season_end)s
                        AND win_loss = %(win_loss)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""

        rankings_df = pd.read_sql(rankings, con=conn, params={'season_end': season_end, 'win_loss': win_loss})


    elif season_end != 'all' and win_loss == 'both' and season_type == "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE season_end = %(season_end)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""

        rankings_df = pd.read_sql(rankings, con=conn, params={'season_end': season_end})


    elif season_end == 'all' and win_loss != 'both' and season_type == "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE win_loss = %(win_loss)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""
        rankings_df = pd.read_sql(rankings, con=conn, params={'win_loss': win_loss})

    
    elif season_end == 'all' and win_loss == 'both' and season_type != "total":
        rankings = """SELECT player_id, player_name, AVG( wc_rank_team ) WIN_RANK
                        FROM all_games_ranked
                        WHERE season_type = %(season_type)s
                        GROUP BY player_id, player_name
                        ORDER BY WIN_RANK;"""

        rankings_df = pd.read_sql(rankings, con=conn, params={'season_type': season_type})

    conn.close()
    return(rankings_df)

def most_improved(df):
    df = df.sort_values(by=['player_id', 'season_type', 'season_end'])
    df = df.reset_index(drop=True)

    df['wc_change'] = 0
    df['wc_il_change'] = 0
    df['tc_change'] = 0
    df['gp_change'] = 0
    for i in range(len(df)):
        if i == 0:
            df.loc[i, 'wc_change'] = 0
            df.loc[i, 'wc_il_change'] = 0
            df.loc[i, 'tc_change'] = 0
            df.loc[i, 'gp_change'] = 0
        elif df.loc[i-1, 'player_id'] == df.loc[i, 'player_id'] and df.loc[i-1, 'season_type'] == df.loc[i, 'season_type']:
            df.loc[i, 'wc_change'] = df.loc[i, 'wins_contr'] - df.loc[i-1, 'wins_contr'] 
            df.loc[i, 'wc_il_change'] = df.loc[i, 'wins_contr_in_loss'] - df.loc[i-1, 'wins_contr_in_loss']
            df.loc[i, 'tc_change'] = (df.loc[i, 'wins_contr'] - df.loc[i-1, 'wins_contr']) + (df.loc[i, 'wins_contr_in_loss'] - df.loc[i-1, 'wins_contr_in_loss'])
            df.loc[i, 'gp_change'] = df.loc[i, 'games_played'] - df.loc[i-1, 'games_played']

        else:
            df.loc[i, 'wc_change'] = 0
            df.loc[i, 'tc_change'] = 0
            df.loc[i, 'wc_il_change'] = 0
            df.loc[i, 'gp_change'] = 0
        
    return df


def compile_yearly_stats():
    wc_df = wins_contributed_basics()
    wc_df = wc_df.append(wc_totals())

    wc_il_df = wins_contributed_in_loss_basics()
    wc_il_df = wc_il_df.append(wc_il_totals())

    yearly_stats_df = wc_df.merge(wc_il_df, on=['season_type', 'season_end', 'player_id', 'player_name'])
    yearly_stats_df = yearly_stats_df.merge(yearly_games_played(), on=['season_type', 'season_end', 'player_id', 'player_name'])
    yearly_stats_df = wc_lc_yearly_ratio(yearly_stats_df)
    yearly_stats_df = yearly_stats_df[['player_id', 'player_name', 'season_end', 'season_type', 'wins_contr', 'avg_wc_il', 'max_wc_il', 'wins_contr_in_loss', 'wins', 'losses', 'games_played', 'wc_lc_ratio', 'avg_wc', 'max_wc']]
    yearly_stats_df['avg_tc'] = (yearly_stats_df['wins_contr'] + yearly_stats_df['wins_contr_in_loss']) / yearly_stats_df['games_played']
    yearly_stats_df['max_tc'] = [ yearly_stats_df.loc[i, 'max_wc_il'] if yearly_stats_df.loc[i, 'max_wc_il'] > yearly_stats_df.loc[i, 'max_wc'] else yearly_stats_df.loc[i, 'max_wc'] for i in range(len(yearly_stats_df)) ]
    yearly_stats_df = most_improved(yearly_stats_df)
    #print(yearly_stats_df.sort_values('wc_change', ascending=False))
    
    sql_table = 'yearly_stats_by_season'
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    yearly_stats_df.to_sql(sql_table, con = engine, if_exists='replace', index=False)
    conn.close()

def compile_team_yearly_stats():
    dc_wc_df = depth_chart_position_by_year_splits().append(depth_chart_position_by_year_total())
    print('dc_wc_df')
    print(dc_wc_df[dc_wc_df['player_id'] == 202355])
    dc_wc_il_df = depth_chart_position_by_year_splits(win_loss=0).append(depth_chart_position_by_year_total(win_loss=0))
    print('dc_wc_il_df')
    print(dc_wc_il_df[dc_wc_il_df['player_id'] == 202355])
    dc_tc_df = depth_chart_position_by_year_splits(win_loss='both').append(depth_chart_position_by_year_total(win_loss='both'))   
    print('dc_tc_df')
    print(dc_tc_df[dc_tc_df['player_id'] == 202355])
    team_yearly_stats = dc_wc_df.merge(dc_wc_il_df, on=['season_type', 'season_end', 'team_id', 'player_id', 'player_name'])  
    team_yearly_stats = team_yearly_stats.merge(dc_tc_df, on=['season_type', 'season_end', 'team_id', 'player_id', 'player_name'])
    print('team_yearly_stats')
    print(team_yearly_stats[team_yearly_stats['player_id'] == 202355])



    team_yearly_stats['wc_rank_team'] = team_yearly_stats['wc_rank_team'].values.astype(int)
    team_yearly_stats['wc_il_rank_team'] = team_yearly_stats['wc_il_rank_team'].values.astype(int)
    team_yearly_stats['tc_rank_team'] = team_yearly_stats['tc_rank_team'].values.astype(int)
    team_yearly_stats['wc_depth_chart_diff'] = team_yearly_stats['wc_depth_chart_diff'].values.astype(float) 
    team_yearly_stats['wc_il_depth_chart_diff'] = team_yearly_stats['wc_il_depth_chart_diff'].values.astype(float)
    team_yearly_stats['tc_depth_chart_diff'] = team_yearly_stats['tc_depth_chart_diff'].values.astype(float)
    team_yearly_stats['season_end'] = team_yearly_stats['season_end'].values.astype(int)
    team_yearly_stats['player_id'] = team_yearly_stats['player_id'].values.astype(int)
    

    #print(team_yearly_stats.info())
    #print(team_yearly_stats.describe())

    sql_table = 'yearly_stats_by_team'
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    team_yearly_stats.to_sql(sql_table, con = engine, if_exists='replace', index=False)
    conn.close()

#compile_team_yearly_stats()
