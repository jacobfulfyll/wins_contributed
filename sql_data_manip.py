import psycopg2 as pg2

conn = pg2.connect(dbname= "jacob_wins", host = "localhost")
cur = conn.cursor()

season_sort = """SELECT player_name,
                        SUM( ROUND( points_score::numeric, 3 ) ) PTS_SCORE,
                        SUM( ROUND( missed_fg_score::numeric, 3) ) MISS_SCORE,
                        SUM( ROUND( ft_score::numeric, 3) ) FT_SCORE,
                        SUM( ROUND( assists_score::numeric, 3) ) AST_SCORE,
                        SUM( ROUND( ft_ast_score::numeric, 3) ) FT_AST,
                        SUM( ROUND( sast_score::numeric, 3) ) SAST_SCORE,
                        SUM( ROUND( orebs_score::numeric, 3) ) OREBS_SCORE,
                        SUM( ROUND( drebs_score::numeric, 3) ) DREBS_SCORE,
                        SUM( ROUND( to_score::numeric, 3) ) TO_SCORE,
                        SUM( ROUND( stls_score::numeric, 3) ) STL_SCORE,
                        SUM( ROUND( blocks_score::numeric, 3) ) BLK_SCORE,
                        SUM( ROUND( dfg_score::numeric, 3) ) DFG_SCORE,
                        SUM( ROUND( def_fouls_score::numeric, 3) ) PF_SCORE,
                        SUM( ROUND( jacob_value::numeric, 3) ) TOTAL_SCORE,
                        SUM( ROUND( wins_contr::numeric, 3) ) WINS
                 FROM jacob_wins_2018_final
                 GROUP BY player_id, player_name
                 ORDER BY OREBS_SCORE DESC;
                 
                                   """

    multi_season_sort = """SELECT player_name,
                        SUM( ROUND( points_score::numeric, 3 ) ) PTS_SCORE,
                        SUM( ROUND( missed_fg_score::numeric, 3) ) MISS_SCORE,
                        SUM( ROUND( ft_score::numeric, 3) ) FT_SCORE,
                        SUM( ROUND( assists_score::numeric, 3) ) AST_SCORE,
                        SUM( ROUND( ft_ast_score::numeric, 3) ) FT_AST,
                        SUM( ROUND( sast_score::numeric, 3) ) SAST_SCORE,
                        SUM( ROUND( orebs_score::numeric, 3) ) OREBS_SCORE,
                        SUM( ROUND( drebs_score::numeric, 3) ) DREBS_SCORE,
                        SUM( ROUND( to_score::numeric, 3) ) TO_SCORE,
                        SUM( ROUND( stls_score::numeric, 3) ) STL_SCORE,
                        SUM( ROUND( blocks_score::numeric, 3) ) BLK_SCORE,
                        SUM( ROUND( dfg_score::numeric, 3) ) DFG_SCORE,
                        SUM( ROUND( def_fouls_score::numeric, 3) ) PF_SCORE,
                        SUM( ROUND( jacob_value::numeric, 3) ) TOTAL_SCORE,
                        SUM( ROUND( wins_contr::numeric, 3) ) WINS
                                FROM(
                                    SELECT *
                                    FROM jacob_wins_2017_final
                                    
                                    UNION ALL

                                    SELECT *
                                    FROM jacob_wins_2018_z
                                    
                                    UNION ALL

                                    SELECT *
                                    FROM jacob_wins_2019_z   ) t
                    GROUP BY t.player_id, t.player_name
                    ORDER BY WINS DESC;
                    """

fix_table = """ CREATE TABLE jacob_wins_2018_z(
 id               SERIAL,
 game_id          character varying(50)             not null,
 team_id          bigint                            not null, 
 opponent_id      bigint                            not null, 
 player_id        bigint                            not null, 
 player_name      character varying(50)             not null, 
 points_score     real                              not null, 
 assists_score    real                              not null, 
 orebs_score      real                              not null, 
 drebs_score      real                              not null, 
 to_score         real                              not null, 
 stls_score       real                              not null, 
 blocks_score     real                              not null, 
 ft_score         real                              not null, 
 dfg_score        real                              not null, 
 sast_score       real                              not null, 
 ft_ast_score     real                              not null, 
 missed_fg_score  real                              not null, 
 def_fouls_score  real                              not null, 
 jacob_value      real                              not null, 
 wins_contr       real                              not null );



INSERT INTO jacob_wins_2018_z (game_id, team_id, opponent_id, player_id, player_name, points_score, assists_score, orebs_score, drebs_score, to_score, stls_score, blocks_score, ft_score, dfg_score, sast_score, ft_ast_score, missed_fg_score, def_fouls_score, jacob_value, wins_contr)
SELECT * FROM jacob_wins_2018_final;
FROM initial_table
                    id SERIAL PRIMARY KEY
             
cur.execute(multi_season_sort)

years = cur.fetchall()
print(years)

#conn.commit()
conn.close()

'''
SELECT player_name, MAX(wins_contr) as Wins 
FROM jacob_wins_2019 
GROUP BY player_name 
ORDER BY Wins DESC;
'''

ALTER TABLE jacob_wins_2018_final
ALTER COLUMN assists_score TYPE FLOAT
USING assists_score::double precision;

ALTER TABLE jacob_wins_2018_final
ALTER COLUMN stls_score TYPE FLOAT
USING stls_score::double precision;

ALTER TABLE jacob_wins_2018_final
ALTER COLUMN blocks_score TYPE FLOAT
USING blocks_score::double precision;

ALTER TABLE jacob_wins_2018_final
ALTER COLUMN ft_ast_score TYPE FLOAT
USING ft_ast_score::double precision;

'''                    UNION ALL
                    SELECT player_name,
                        SUM( ROUND( points_score::numeric, 3 ) ) PTS_SCORE,
                        SUM( ROUND( missed_fg_score::numeric, 3) ) MISS_SCORE,
                        SUM( ROUND( ft_score::numeric, 3) ) FT_SCORE,
                        SUM( ROUND( assists_score::numeric, 3) ) AST_SCORE,
                        SUM( ROUND( ft_ast_score::numeric, 3) ) FT_AST,
                        SUM( ROUND( sast_score::numeric, 3) ) SAST_SCORE,
                        SUM( ROUND( orebs_score::numeric, 3) ) OREBS_SCORE,
                        SUM( ROUND( drebs_score::numeric, 3) ) DREBS_SCORE,
                        SUM( ROUND( to_score::numeric, 3) ) TO_SCORE,
                        SUM( ROUND( stls_score::numeric, 3) ) STL_SCORE,
                        SUM( ROUND( blocks_score::numeric, 3) ) BLK_SCORE,
                        SUM( ROUND( dfg_score::numeric, 3) ) DFG_SCORE,
                        SUM( ROUND( def_fouls_score::numeric, 3) ) PF_SCORE,
                        SUM( ROUND( jacob_value::numeric, 3) ) TOTAL_SCORE,
                        SUM( ROUND( wins_contr::numeric, 3) ) WINS
                    FROM jacob_wins_2018_minutes
                    GROUP BY player_id, jacob_wins_2018_minutes.player_name 
                    UNION ALL
                    SELECT player_name,
                        SUM( ROUND( points_score::numeric, 3 ) ) PTS_SCORE,
                        SUM( ROUND( missed_fg_score::numeric, 3) ) MISS_SCORE,
                        SUM( ROUND( ft_score::numeric, 3) ) FT_SCORE,
                        SUM( ROUND( assists_score::numeric, 3) ) AST_SCORE,
                        SUM( ROUND( ft_ast_score::numeric, 3) ) FT_AST,
                        SUM( ROUND( sast_score::numeric, 3) ) SAST_SCORE,
                        SUM( ROUND( orebs_score::numeric, 3) ) OREBS_SCORE,
                        SUM( ROUND( drebs_score::numeric, 3) ) DREBS_SCORE,
                        SUM( ROUND( to_score::numeric, 3) ) TO_SCORE,
                        SUM( ROUND( stls_score::numeric, 3) ) STL_SCORE,
                        SUM( ROUND( blocks_score::numeric, 3) ) BLK_SCORE,
                        SUM( ROUND( dfg_score::numeric, 3) ) DFG_SCORE,
                        SUM( ROUND( def_fouls_score::numeric, 3) ) PF_SCORE,
                        SUM( ROUND( jacob_value::numeric, 3) ) TOTAL_SCORE,
                        SUM( ROUND( wins_contr::numeric, 3) ) WINS
                    FROM jacob_wins_2019_minutes 
                    GROUP BY player_id, jacob_wins_2019_minutes.player_name'''