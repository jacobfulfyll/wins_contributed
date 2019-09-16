#Only need to run one time to set up all your tables in your database
import psycopg2 as pg2

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

tables = """CREATE TABLE playoffs_2016_17 (id SERIAL PRIMARY KEY,
                                        game_id VARCHAR(50) NOT NULL,
                                        win_loss INT NOT NULL,
                                        team_id BIGINT NOT NULL,
                                        opponent_id BIGINT NOT NULL,
                                        player_id BIGINT NOT NULL,
                                        player_name VARCHAR(50) NOT NULL,
                                        points_score REAL NOT NULL,
                                        assists_score REAL NOT NULL,
                                        orebs_score REAL NOT NULL,
                                        drebs_score REAL NOT NULL,
                                        to_score REAL NOT NULL,
                                        stls_score REAL NOT NULL,
                                        blocks_score REAL NOT NULL,
                                        ft_score REAL NOT NULL,
                                        dfg_score REAL NOT NULL,
                                        sast_score REAL NOT NULL,
                                        ft_ast_score REAL NOT NULL,
                                        missed_fg_score REAL NOT NULL,
                                        def_fouls_score REAL NOT NULL,
                                        jacob_value REAL NOT NULL,
                                        wins_contr REAL NOT NULL);
                                   """
             
cur.execute(tables)
conn.commit()

play_by_play="""CREATE TABLE playoff_events_2016_17 (id SERIAL PRIMARY KEY,
                                game_id VARCHAR(50) NOT NULL, 
                                eventnum INTEGER NULL,
                                eventmsgtype INTEGER NULL,
                                homedescription VARCHAR(200) NULL,
                                visitordescription VARCHAR(200) NULL,
                                player1_name VARCHAR(50) NULL,
                                player2_name VARCHAR(50) NULL,
                                player1_id BIGINT NULL,
                                player2_id BIGINT NULL,
                                player1_team_id BIGINT NULL,
                                player2_team_id BIGINT NULL);"""

cur.execute(play_by_play)
conn.commit()

general="""CREATE TABLE playoff_totals_2016_17 (id SERIAL PRIMARY KEY,
                                PLAYER_ID BIGINT NOT NULL,
                                PLAYER_NAME VARCHAR(50) NOT NULL, 
                                MIN VARCHAR(7) NULL,
                                FG3M INTEGER NULL,
                                FTM INTEGER NULL,
                                FTA INTEGER NULL,
                                AST INTEGER NULL,
                                STL INTEGER NULL,
                                BLK INTEGER NULL,
                                OREB INTEGER NULL,
                                DREB INTEGER NULL,
                                TOS INTEGER NULL,
                                SAST INTEGER NULL,
                                FTAST INTEGER NULL,
                                DFGM INTEGER NULL,
                                DFGA INTEGER NULL,
                                PCT_UAST_2PM INTEGER NULL,
                                PCT_UAST_3PM INTEGER NULL,
                                PTS_2ND_CHANCE INTEGER NULL,
                                defense_factor REAL NULL,
                                defense_factor2 REAL NULL,
                                offense_factor REAL NULL,
                                offense_factor2 REAL NULL,
                                FG2M INTEGER NULL,
                                DFG INTEGER NULL,
                                SEC_FACT REAL NULL);"""
                              
cur.execute(general)
conn.commit()

conn.close()