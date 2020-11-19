import psycopg2 as pg2
import pandas as pd



def get_reg_season_2018_19():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2018_19
            WHERE season_type = 'Regular Season';"""

    reg_season_2018_19 = pd.read_sql(df, con=conn)
    reg_season_2018_19['season_type'] = 'Regular Season'
    reg_season_2018_19['season_end'] = 2019
    conn.close()

    return reg_season_2018_19

def get_reg_season_2017_18():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2017_18
            WHERE season_type = 'Regular Season';"""

    reg_season_2017_18 = pd.read_sql(df, con=conn)
    reg_season_2017_18['season_end'] = 2018
    conn.close()

    return reg_season_2017_18

def get_reg_season_2016_17():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2016_17
            WHERE season_type = 'Regular Season';"""

    reg_season_2016_17 = pd.read_sql(df, con=conn)
    reg_season_2016_17['season_end'] = 2017
    conn.close()

    return reg_season_2016_17

def get_reg_season_2015_16():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2015_16
            WHERE season_type = 'Regular Season';"""

    reg_season_2015_16 = pd.read_sql(df, con=conn)
    reg_season_2015_16['season_end'] = 2016
    conn.close()

    return reg_season_2015_16

def get_reg_season_2014_15():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2014_15
            WHERE season_type = 'Regular Season';"""

    reg_season_2014_15 = pd.read_sql(df, con=conn)
    reg_season_2014_15['season_end'] = 2015
    conn.close()

    return reg_season_2014_15

def get_reg_season_2013_14():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2013_14
            WHERE season_type = 'Regular Season';"""

    reg_season_2013_14 = pd.read_sql(df, con=conn)
    reg_season_2013_14['season_end'] = 2014
    conn.close()

    return reg_season_2013_14

def get_playoffs_2018_19():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2018_19
            WHERE season_type = 'Playoffs';"""

    playoffs_2018_19 = pd.read_sql(df, con=conn)
    playoffs_2018_19['season_end'] = 2019
    conn.close()

    return playoffs_2018_19

def get_playoffs_2017_18():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2017_18
            WHERE season_type = 'Playoffs';"""

    playoffs_2017_18 = pd.read_sql(df, con=conn)
    playoffs_2017_18['season_end'] = 2018
    conn.close()

    return playoffs_2017_18

def get_playoffs_2016_17():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2016_17
            WHERE season_type = 'Playoffs';"""

    playoffs_2016_17 = pd.read_sql(df, con=conn)
    playoffs_2016_17['season_end'] = 2017
    conn.close()

    return playoffs_2016_17

def get_playoffs_2015_16():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2015_16
            WHERE season_type = 'Playoffs';"""

    playoffs_2015_16 = pd.read_sql(df, con=conn)
    playoffs_2015_16['season_end'] = 2016
    conn.close()

    return playoffs_2015_16

def get_playoffs_2014_15():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2014_15
            WHERE season_type = 'Playoffs';"""

    playoffs_2014_15 = pd.read_sql(df, con=conn)
    playoffs_2014_15['season_end'] = 2015
    conn.close()

    return playoffs_2014_15

def get_playoffs_2013_14():
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    df = """SELECT *
            FROM value_contributed_2013_14
            WHERE season_type = 'Playoffs';"""

    playoffs_2013_14 = pd.read_sql(df, con=conn)
    playoffs_2013_14['season_end'] = 2014
    conn.close()

    return playoffs_2013_14

def create_stats_df():
    reg_season_2018_19 = get_reg_season_2018_19()
    reg_season_2017_18 = get_reg_season_2017_18()
    reg_season_2016_17 = get_reg_season_2016_17()
    reg_season_2015_16 = get_reg_season_2015_16()
    reg_season_2014_15 = get_reg_season_2014_15()
    reg_season_2013_14 = get_reg_season_2013_14()

    playoffs_2018_19 = get_playoffs_2018_19()
    playoffs_2017_18 = get_playoffs_2017_18()
    playoffs_2016_17 = get_playoffs_2016_17()
    playoffs_2015_16 = get_playoffs_2015_16()
    playoffs_2014_15 = get_playoffs_2014_15()
    playoffs_2013_14 = get_playoffs_2013_14()

    all_time_df = reg_season_2018_19.append([reg_season_2017_18, reg_season_2016_17, reg_season_2015_16, 
                                                reg_season_2014_15, reg_season_2013_14, playoffs_2018_19, 
                                                playoffs_2017_18, playoffs_2016_17, playoffs_2015_16, 
                                                playoffs_2014_15, playoffs_2013_14])

    all_time_df = all_time_df.rename(columns={"value_contributed": "wins_contr", "total_value": "jacob_value"})
    return(all_time_df)
