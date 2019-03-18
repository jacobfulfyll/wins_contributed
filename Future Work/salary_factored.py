import psycopg2 as pg2
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from time import sleep
from classes.teamgamelog import TeamGameLog

conn = pg2.connect(dbname= "jacob_wins", host = "localhost")
cur = conn.cursor()

season_sort = """SELECT player_name AS player,
                        SUM( ROUND( jacob_value::numeric, 3) ) TOTAL_SCORE,
                        SUM( ROUND( wins_contr::numeric, 3) ) WINS
                 FROM jacob_wins_2018_fix
                 GROUP BY player_id, player_name
                 ORDER BY WINS DESC;"""

                                                  

season_df = pd.read_sql(season_sort, con=conn)

conn.close()

salary_df = pd.read_csv('nba_salaries_1990_to_2018.csv')
salary_df = salary_df[salary_df['season_end'] == 2018]
salary_df = salary_df[['player', 'salary']]

print(type(season_df['player']))
print('======================')
print('======================')
print('======================')
print(type(salary_df))
print('======================')
print('======================')
print('======================')


new = pd.merge(salary_df, season_df, on='player')
new['salary_adj'] = new['salary'] / 1000000
new['Pay_Per_Win'] = new['salary_adj'] / new['wins']
new = new.sort_values(by='salary', ascending=False)

print(new.head(50))