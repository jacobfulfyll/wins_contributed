#Only need to run one time to set up all your tables in your database
import psycopg2 as pg2

conn = pg2.connect(dbname= "wins_contr", host = "localhost")
cur = conn.cursor()

value_contributed = """CREATE TABLE value_contributed_2019_20 (id SERIAL PRIMARY KEY,
                                        game_id VARCHAR(50) NOT NULL,
                                        win_loss INT NOT NULL,
                                        team_id BIGINT NOT NULL,
                                        opponent_id BIGINT NOT NULL,
                                        player_id BIGINT NOT NULL,
                                        player_name VARCHAR(50) NOT NULL,
                                        two_pt_score_uast REAL NOT NULL,
                                        three_pt_score_uast REAL NOT NULL,
                                        two_pt_score_ast REAL NOT NULL,
                                        three_pt_score_ast REAL NOT NULL,
                                        two_pt_score_uast_oreb REAL NOT NULL,
                                        three_pt_score_uast_oreb REAL NOT NULL,
                                        two_pt_score_ast_oreb REAL NOT NULL,
                                        three_pt_score_ast_oreb REAL NOT NULL,
                                        ast_2pt REAL NOT NULL,
                                        ast_3pt REAL NOT NULL,
                                        ast_two_pt_oreb REAL NOT NULL,
                                        ast_three_pt_oreb REAL NOT NULL,
                                        oreb_two_pt_uast REAL NOT NULL,
                                        oreb_two_pt_ast REAL NOT NULL,
                                        oreb_three_pt_uast REAL NOT NULL,
                                        oreb_three_pt_ast REAL NOT NULL,
                                        oreb_ft REAL NOT NULL,
                                        dreb_blk REAL NOT NULL,
                                        dreb_no_blk REAL NOT NULL,
                                        to_score REAL NOT NULL,
                                        stls_score REAL NOT NULL,
                                        blks_score REAL NOT NULL,
                                        positive_ft REAL NOT NULL,
                                        negative_ft REAL NOT NULL,
                                        dfg_score REAL NOT NULL,
                                        sast_score REAL NOT NULL,
                                        ft_ast_score REAL NOT NULL,
                                        missed_two_pt_fg REAL NOT NULL,
                                        missed_three_pt_fg REAL NOT NULL,
                                        positive_def_fouls REAL NOT NULL,
                                        negative_def_fouls REAL NOT NULL,
                                        total_value REAL NOT NULL,
                                        normalized_value REAL NOT NULL,
                                        factored_value REAL NOT NULL,
                                        value_contributed REAL NOT NULL,
                                        season_type VARCHAR(20) NOT NULL);
                                   """
             
cur.execute(value_contributed)
conn.commit()


play_by_play="""CREATE TABLE play_by_play_2019_20 (id SERIAL PRIMARY KEY,
                                game_id VARCHAR(50) NOT NULL, 
                                eventnum INTEGER NULL,
                                eventmsgtype INTEGER NULL,
                                winningteam VARCHAR(200) NULL,
                                losingteam VARCHAR(200) NULL,
                                player1_name VARCHAR(50) NULL,
                                player2_name VARCHAR(50) NULL,
                                player1_id BIGINT NULL,
                                player2_id BIGINT NULL,
                                player1_team_id BIGINT NULL,
                                player2_team_id BIGINT NULL,
                                season_type varchar(20) NOT NULL);"""

cur.execute(play_by_play)
conn.commit()

val_contr_inputs="""CREATE TABLE val_contr_inputs_2019_20 (id SERIAL PRIMARY KEY,
                                PLAYER_ID BIGINT NOT NULL,
                                PLAYER_NAME VARCHAR(50) NOT NULL,
                                TEAM_ID BIGINT NULL,
                                SEC_FACT REAL NULL,
                                FG2_MADE INTEGER NULL,
                                FG2_MISSED INTEGER NULL,
                                FG3_MADE INTEGER NULL,
                                FG3_MISSED INTEGER NULL,
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
                                DFG INTEGER NULL,
                                PCT_UAST_2PM INTEGER NULL,
                                PCT_UAST_3PM INTEGER NULL,
                                PTS_2ND_CHANCE INTEGER NULL,
                                defense_factor REAL NULL,
                                offense_factor REAL NULL,
                                SEASON_TYPE VARCHAR(20) NOT NULL);"""
                              
cur.execute(val_contr_inputs)
conn.commit()

possessional_adjustments="""CREATE TABLE possessional_adjustments_2019_20 (id SERIAL PRIMARY KEY,
                                game_id VARCHAR(50) NOT NULL,
                                win_loss INT NOT NULL,
                                TEAM_ID BIGINT NULL,
                                opponent_id BIGINT NULL,
                                PLAYER_ID BIGINT NOT NULL,
                                PLAYER_NAME VARCHAR(50) NOT NULL,
                                orebs_no_score INTEGER NOT NULL,
                                failed_blks INTEGER NOT NULL,
                                missed_two_pt_fg_possession INTEGER NOT NULL,
                                missed_three_pt_fg_possession INTEGER NOT NULL,
                                SEASON_TYPE VARCHAR(20) NOT NULL);"""
                              
cur.execute(possessional_adjustments)
conn.commit()

conn.close()