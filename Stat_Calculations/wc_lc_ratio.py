import psycopg2 as pg2
import pandas as pd

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

win_mean = """SELECT player_id, player_name, AVG( ROUND( wins_contr::numeric, 3) ) WINS_WC
                 FROM reg_season_2018_19
                 WHERE win_loss = 1
                 GROUP BY player_id, player_name
                 ORDER BY WINS_WC DESC;"""

loss_mean = """SELECT player_id, AVG( ROUND( wins_contr::numeric, 3) ) LOSSES_WC
                 FROM reg_season_2018_19
                 WHERE win_loss = 0
                 GROUP BY player_id
                 ORDER BY LOSSES_WC DESC;"""

win_df = pd.read_sql(win_mean, con=conn)
loss_df = pd.read_sql(loss_mean, con=conn)
print(win_df)
print(loss_df)
conn.close()

ratio_df = win_df.merge(loss_df, on='player_id')
ratio_df['wc_ratio'] = ratio_df['wins_wc'] / ratio_df['losses_wc']
print(ratio_df.sort_values(by='wc_ratio', ascending=False))