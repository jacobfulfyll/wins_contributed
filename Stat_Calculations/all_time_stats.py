import pandas as pd
from yearly_stats import compile_team_yearly_stats, wins_contributed_basics, wins_contributed_in_loss_basics, yearly_games_played
from compile_data import create_stats_df
import numpy as np
import psycopg2 as pg2
from sqlalchemy import create_engine

master_df = create_stats_df()

def seasons_played():
    all_time_df = wins_contributed_basics()
    reg_seasons_df = all_time_df[all_time_df['season_type'] == "Regular Season"]
    reg_seasons_df = reg_seasons_df[['player_id', 'player_name', 'season_end']].groupby(['player_id', 'player_name'], as_index=False)
    reg_seasons_df = reg_seasons_df.count()
    reg_seasons_df = reg_seasons_df.rename(columns={"season_end": "reg_seasons_played"})
    reg_seasons_list = []
    for idx, x in all_time_df['player_id'].iteritems():
        try:
            reg_seasons_list.append(reg_seasons_df[reg_seasons_df['player_id'] == x].reset_index(drop=True).loc[0, 'reg_seasons_played'])
        except:
            reg_seasons_list.append(0)

    all_time_df['reg_seasons_played'] = reg_seasons_list

    all_time_df = all_time_df[['player_id', 'player_name','reg_seasons_played']]

    return all_time_df

seasons_played()

def playoffs_played():
    all_time_df = wins_contributed_basics()
    playoffs_df = all_time_df[all_time_df['season_type'] == "Playoffs"]
    playoffs_df = playoffs_df[['player_id', 'player_name', 'season_end']].groupby(['player_id', 'player_name'], as_index=False)
    playoffs_df = playoffs_df.count()
    playoffs_df = playoffs_df.rename(columns={"season_end": "playoffs_played"})
    playoffs_df = playoffs_df[['player_id', 'player_name', 'playoffs_played']]

    playoffs_list = []
    for idx, x in all_time_df['player_id'].iteritems():
        try:
            playoffs_list.append(playoffs_df[playoffs_df['player_id'] == x].reset_index(drop=True).loc[0, 'playoffs_played'])
        except:
            playoffs_list.append(0)

    all_time_df['playoffs_played'] = playoffs_list
    all_time_df = all_time_df[['player_id', 'player_name', 'playoffs_played']]
  
    return all_time_df

#playoffs_played()

def games_played():
    df = yearly_games_played()
   
    playoffs_df = df[df['season_type'] == 'Playoffs']
    reg_season_df = df[df['season_type'] == 'Regular Season']
    totals_df = df

    
    playoffs_df = playoffs_df.groupby(['season_type', 'player_id', 'player_name'], as_index=False).sum().sort_values('wins')
    reg_season_df = reg_season_df.groupby(['season_type', 'player_id', 'player_name'], as_index=False).sum().sort_values('wins')
    totals_df = totals_df.groupby(['player_id', 'player_name'], as_index=False).sum().sort_values('wins')
    totals_df['season_type'] = 'Total'
    
    games_played_df = reg_season_df.append([totals_df, playoffs_df])

    return games_played_df[['player_id', 'player_name', 'season_type', 'games_played', 'wins', 'losses']]


def all_time_wc(wins_contributed_df, reg_seasons_df, playoffs_df):
    
    all_time_df = wins_contributed_df
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr']].groupby(['player_id','player_name'], as_index=False)
    

    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr": "max_season_wc"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Total'

    # Compute Total All-Time Avg WC
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()

    all_time_df['avg_wc'] = all_time_df['wins_contr'] / all_time_df['reg_seasons_played']
    

    return all_time_df


def all_time_playoff_wc(wins_contributed_df, reg_seasons_df, playoffs_df):
    all_time_df = wins_contributed_df
    all_time_df = all_time_df[all_time_df['season_type'] == 'Playoffs']
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr']].groupby(['player_id','player_name'], as_index=False)
    
    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr": "max_season_wc"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Playoffs'

    # Compute Total All-Time Avg WC_playoffs
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df['avg_wc'] = all_time_df['wins_contr'] / all_time_df['playoffs_played']
    
    return all_time_df

def all_time_reg_season_wc(wins_contributed_df, reg_seasons_df, playoffs_df):
    all_time_df = wins_contributed_df
    all_time_df = all_time_df[all_time_df['season_type'] == 'Regular Season']
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr']].groupby(['player_id','player_name'], as_index=False)
    
    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr": "max_season_wc"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Regular Season'

    # Compute Total All-Time Avg WC
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df['avg_wc'] = all_time_df['wins_contr'] / all_time_df['reg_seasons_played']

    return all_time_df

def all_time_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df):
    all_time_df = wins_contributed_in_loss_df
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss']].groupby(['player_id','player_name'], as_index=False)
    
    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr_in_loss": "max_season_wc_il"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr_in_loss', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Total'
    

    # Compute Total All-Time Avg WC
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df['avg_wc_il'] = all_time_df['wins_contr_in_loss'] / all_time_df['reg_seasons_played']

    return all_time_df



def all_time_playoff_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df):
    all_time_df = wins_contributed_in_loss_df
    all_time_df = all_time_df[all_time_df['season_type'] == 'Playoffs']
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss']].groupby(['player_id','player_name'], as_index=False)
    
    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr_in_loss": "max_season_wc_il"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr_in_loss', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Playoffs'
    
    # Compute Total All-Time Avg WC
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df['avg_wc_il'] = all_time_df['wins_contr_in_loss'] / all_time_df['playoffs_played']

    return all_time_df

def all_time_reg_season_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df):
    all_time_df = wins_contributed_in_loss_df
    all_time_df = all_time_df[all_time_df['season_type'] == 'Regular Season']
    all_time_df_max = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss', 'season_end']].groupby(['player_id','player_name','season_end'], as_index=False)
    all_time_df = all_time_df[['player_id', 'player_name', 'wins_contr_in_loss']].groupby(['player_id','player_name'], as_index=False)
    
    all_time_df_max = all_time_df_max.sum()
    all_time_df_max = all_time_df_max.groupby(['player_id', 'player_name']).max()
    all_time_df_max = all_time_df_max.rename(columns={"wins_contr_in_loss": "max_season_wc_il"})
    all_time_df_sum = all_time_df.aggregate(np.sum)

    all_time_df = all_time_df_max.merge(all_time_df_sum, on=['player_id', 'player_name'])

    all_time_df = all_time_df.sort_values('wins_contr_in_loss', ascending=False)
    all_time_df = all_time_df.reset_index(drop=True)
    all_time_df['season_type'] = 'Regular Season'

    # Compute Total All-Time Avg WC
    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()
    all_time_df['avg_wc_il'] = all_time_df['wins_contr_in_loss'] / all_time_df['reg_seasons_played']

    return all_time_df


def compile_wc_totals():
    reg_seasons_df = seasons_played()
    playoffs_df = playoffs_played()
    wins_contributed_df = wins_contributed_basics()
    wins_contributed_in_loss_df = wins_contributed_in_loss_basics()

    df1 = all_time_wc(wins_contributed_df, reg_seasons_df, playoffs_df)
    df2 = all_time_playoff_wc(wins_contributed_df, reg_seasons_df, playoffs_df)
    df3 = all_time_reg_season_wc(wins_contributed_df, reg_seasons_df, playoffs_df)
    df4 = all_time_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df)
    df5 = all_time_playoff_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df)
    df6 = all_time_reg_season_wc_il(wins_contributed_in_loss_df, reg_seasons_df, playoffs_df)

    wc_totals_compiled = df1.append([df2, df3])
    wc_il_totals_compiled = df4.append([df5, df6])

    totals_compiled = wc_totals_compiled.merge(wc_il_totals_compiled, on=['season_type', 'player_id', 'player_name'])
    totals_compiled = totals_compiled[['player_id', 'season_type', 'player_name', 'wins_contr', 'wins_contr_in_loss', 'avg_wc', 'avg_wc_il', 'max_season_wc', 'max_season_wc_il']]
    totals_compiled = totals_compiled.drop_duplicates()

    print('================== Totals Compiled ====================')
    print(totals_compiled)

    return reg_seasons_df, playoffs_df, totals_compiled


def wc_lc_all_time_ratio(df):
    df['wc_lc_ratio'] = df['wins_contr'] / df['wins_contr_in_loss']
    #df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['wc_lc_ratio'], how="all")
    #df = df[(df['wins_contr'] > 2) & (df['season_type'] == 'Playoffs')]
    #print(df.sort_values(by='wc_lc_ratio', ascending=False))
    return df

def all_time_ranking_discrepancy():
    all_time_df = compile_team_yearly_stats().groupby(['season_type', 'player_id', 'player_name'], as_index=False)
    all_time_df = all_time_df.aggregate(np.mean)
    print(all_time_df.sort_values('wc_depth_chart_diff', ascending=False))

#all_time_ranking_discrepancy()

def compile_all_time_stats():
    reg_seasons_df, playoffs_df, all_time_df = compile_wc_totals()

    all_time_df = wc_lc_all_time_ratio(all_time_df)

    all_time_df = all_time_df.merge(reg_seasons_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()

    all_time_df = all_time_df.merge(playoffs_df, on=['player_id', 'player_name'])
    all_time_df = all_time_df.drop_duplicates()

    all_time_df = all_time_df.merge(games_played(), on=['season_type', 'player_id', 'player_name'])

    all_time_df['avg_contr_game'] = (all_time_df['wins_contr'] + all_time_df['wins_contr_in_loss']) / all_time_df['games_played']
    all_time_df = all_time_df.drop_duplicates()
    all_time_df = all_time_df.reset_index(drop=True)

    sql_table = 'all_time_stats'
    conn = pg2.connect(dbname = 'postgres', host = "localhost")
    conn.autocommit = True
    engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/wins_contr')
    all_time_df.to_sql(sql_table, con = engine, index=False, if_exists='replace')
    conn.close()
    
compile_all_time_stats()