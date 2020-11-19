
import psycopg2 as pg2
import pandas as pd
from sqlalchemy import create_engine


season_totals_df = pd.DataFrame(columns=['player_id', 'player_name', 'season_end', 'Value Contributed (Total)', 'Value Contributed (Wins)', 'Value Contributed(Losses)'])


# Options

season_start = 2014
season_end = 2019
season_type = 'all' #'Regular Season', 'Playoffs'
stat_type = 'Totals' # 'Averages', 'Max'


conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

value_contributed_query = """SELECT totals.player_name, total_value_contributed, wins_value_contributed, losses_value_contributed, total_discrepancy, wins_discrepancy, losses_discrepancy, total_avg_rank, wins_avg_rank, losses_avg_rank
                    FROM (
                        SELECT vc.player_id, vc.player_name, SUM(vc.value_contributed) as total_value_contributed, SUM(dd.discrepancy_total) as total_discrepancy, AVG(dd.depth_chart_rank) as total_avg_rank
                        FROM all_seasons_value_contributed as vc
                        INNER JOIN all_seasons_discrepancy_depth as dd
                        ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
                        WHERE vc.season_end >= %(season_start)s
                        AND vc.season_end <= %(season_end)s
                        GROUP BY vc.player_id, vc.player_name) AS totals
                        INNER JOIN (
                            SELECT vc.player_id, vc.player_name, SUM(vc.value_contributed) as losses_value_contributed, SUM(dd.discrepancy_total) as losses_discrepancy, AVG(dd.depth_chart_rank) as losses_avg_rank
                            FROM all_seasons_value_contributed as vc
                            INNER JOIN all_seasons_discrepancy_depth as dd
                            ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
                            WHERE vc.win_loss = 0
                            AND vc.season_end >= %(season_start)s
                            AND vc.season_end <= %(season_end)s
                            GROUP BY vc.player_id, vc.player_name) as losses
                        ON (totals.player_id = losses.player_id AND totals.player_name = losses.player_name)
                        INNER JOIN (
                            SELECT vc.player_id, vc.player_name, SUM(vc.value_contributed) as wins_value_contributed, SUM(dd.discrepancy_total) as wins_discrepancy, AVG(dd.depth_chart_rank) as wins_avg_rank
                            FROM all_seasons_value_contributed as vc
                            INNER JOIN all_seasons_discrepancy_depth as dd
                            ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
                            WHERE vc.win_loss = 1
                            AND vc.season_end >= %(season_start)s
                            AND vc.season_end <= %(season_end)s
                            GROUP BY vc.player_id, vc.player_name) as wins
                        ON (totals.player_id = wins.player_id AND totals.player_name = wins.player_name)
                    ORDER BY total_value_contributed DESC
                    ;"""

value_contributed_df = pd.read_sql(value_contributed_query, con=conn, params={'season_start': season_start, 'season_end': season_end})

value_contributed_df['Value Ratio'] = (value_contributed_df['wins_value_contributed'] + 1) / (value_contributed_df['losses_value_contributed'] + 1) / value_contributed_df['total_avg_rank']
value_contributed_df['Wins - Losses'] = value_contributed_df['wins_value_contributed'] - value_contributed_df['losses_value_contributed']

print(value_contributed_df.sort_values(by='Value Ratio', ascending=False).reset_index(drop=True)[0:50])

# wins_value_contributed_query = """SELECT vc.player_name, SUM(vc.value_contributed) as losses_value_contributed, SUM(dd.discrepancy_total) as losses_discrepancy, AVG(dd.depth_chart_rank) as losses_avg_rank
#                     FROM all_seasons_value_contributed as vc
#                     INNER JOIN all_seasons_discrepancy_depth as dd
#                     ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
#                     WHERE vc.win_loss = 1
#                     AND vc.season_end >= %(season_start)s
#                     AND vc.season_end <= %(season_end)s
#                     GROUP BY vc.player_id, vc.player_name
#                     ORDER BY total_discrepancy DESC;"""

# wins_value_contributed_df = pd.read_sql(wins_value_contributed_query, con=conn, params={'season_start': season_start, 'season_end': season_end})

# print(wins_value_contributed_df)

# losses_value_contributed_query = """SELECT vc.player_name, SUM(vc.value_contributed) as wins_value_contributed, SUM(dd.discrepancy_total) as wins_discrepancy, AVG(dd.depth_chart_rank) as wins_avg_rank
#                     FROM all_seasons_value_contributed as vc
#                     INNER JOIN all_seasons_discrepancy_depth as dd
#                     ON (vc.player_id = dd.player_id AND vc.player_name = dd.player_name AND  vc.game_id = dd.game_id)
#                     WHERE vc.win_loss = 0
#                     AND vc.season_end >= %(season_start)s
#                     AND vc.season_end <= %(season_end)s
#                     GROUP BY vc.player_id, vc.player_name
#                     ORDER BY total_discrepancy DESC;"""

# losses_value_contributed_df = pd.read_sql(losses_value_contributed_query, con=conn, params={'season_start': season_start, 'season_end': season_end})

# print(losses_value_contributed_df)


conn.close()




