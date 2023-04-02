import psycopg2 as pg2
import pandas as pd
from sqlalchemy import create_engine


conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()


df_2021 = """SELECT *
            FROM value_contributed_2020_21;"""

df_2021 = pd.read_sql(df_2021, con=conn)
df_2021['season_end'] = 2021

df_2020 = """SELECT *
            FROM value_contributed_2019_20;"""

df_2020 = pd.read_sql(df_2020, con=conn)
df_2020['season_end'] = 2020

# df_2019 = """SELECT *
#             FROM value_contributed_2018_19;"""

# df_2019 = pd.read_sql(df_2019, con=conn)
# df_2019['season_end'] = 2019

# df_2018 = """SELECT *
#             FROM value_contributed_2017_18;"""

# df_2018 = pd.read_sql(df_2018, con=conn)
# df_2018['season_end'] = 2018

# df_2017 = """SELECT *
#             FROM value_contributed_2016_17;"""

# df_2017 = pd.read_sql(df_2017, con=conn)
# df_2017['season_end'] = 2017

# df_2016 = """SELECT *
#             FROM value_contributed_2015_16;"""

# df_2016 = pd.read_sql(df_2016, con=conn)
# df_2016['season_end'] = 2016

# df_2015 = """SELECT *
#             FROM value_contributed_2014_15;"""

# df_2015 = pd.read_sql(df_2015, con=conn)
# df_2015['season_end'] = 2015

# df_2014 = """SELECT *
#             FROM value_contributed_2013_14;"""

# df_2014 = pd.read_sql(df_2014, con=conn)
# df_2014['season_end'] = 2014

# all_seasons = """CREATE TABLE all_seasons_value_contributed (id SERIAL PRIMARY KEY,
#                                         game_id VARCHAR(50) NOT NULL,
#                                         win_loss INT NOT NULL,
#                                         team_id BIGINT NOT NULL,
#                                         opponent_id BIGINT NOT NULL,
#                                         player_id BIGINT NOT NULL,
#                                         player_name VARCHAR(50) NOT NULL,
#                                         two_pt_score_uast REAL NOT NULL,
#                                         three_pt_score_uast REAL NOT NULL,
#                                         two_pt_score_ast REAL NOT NULL,
#                                         three_pt_score_ast REAL NOT NULL,
#                                         two_pt_score_uast_oreb REAL NOT NULL,
#                                         three_pt_score_uast_oreb REAL NOT NULL,
#                                         two_pt_score_ast_oreb REAL NOT NULL,
#                                         three_pt_score_ast_oreb REAL NOT NULL,
#                                         ast_2pt REAL NOT NULL,
#                                         ast_3pt REAL NOT NULL,
#                                         ast_two_pt_oreb REAL NOT NULL,
#                                         ast_three_pt_oreb REAL NOT NULL,
#                                         oreb_two_pt_uast REAL NOT NULL,
#                                         oreb_two_pt_ast REAL NOT NULL,
#                                         oreb_three_pt_uast REAL NOT NULL,
#                                         oreb_three_pt_ast REAL NOT NULL,
#                                         oreb_ft REAL NOT NULL,
#                                         dreb_blk REAL NOT NULL,
#                                         dreb_no_blk REAL NOT NULL,
#                                         to_score REAL NOT NULL,
#                                         stls_score REAL NOT NULL,
#                                         blks_score REAL NOT NULL,
#                                         positive_ft REAL NOT NULL,
#                                         negative_ft REAL NOT NULL,
#                                         dfg_score REAL NOT NULL,
#                                         sast_score REAL NOT NULL,
#                                         ft_ast_score REAL NOT NULL,
#                                         missed_two_pt_fg REAL NOT NULL,
#                                         missed_three_pt_fg REAL NOT NULL,
#                                         positive_def_fouls REAL NOT NULL,
#                                         negative_def_fouls REAL NOT NULL,
#                                         total_value REAL NOT NULL,
#                                         normalized_value REAL NOT NULL,
#                                         factored_value REAL NOT NULL,
#                                         value_contributed REAL NOT NULL,
#                                         season_type VARCHAR(20) NOT NULL,
#                                         season_end INTEGER NOT NULL);
#                                    """
             
# cur.execute(all_seasons)
# conn.commit()

conn.close()

all_years_df = df_2020.append([df_2021])

all_years_df = all_years_df.drop(columns='id').reset_index(drop=True)

conn = pg2.connect(dbname = 'personal_website', host = "localhost")
conn.autocommit = True
engine = create_engine('postgresql+psycopg2://jacobpress:bocaj29@localhost/personal_website')
all_years_df.to_sql('all_seasons_value_contributed', con = engine, if_exists= "append", index=False)
conn.close()



