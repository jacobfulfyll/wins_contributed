import pandas as pd
import psycopg2 as pg2
import seaborn as sns
import matplotlib.pyplot as plt

def projected_team_graphs():
    team_ids = {'Atlanta Hawks': 1610612737, 'Boston Celtics': 1610612738, 'Brooklyn Nets': 1610612751,
                'Charlotte Hornets': 1610612766, 'Chicago Bulls': 1610612741, 'Cleveland Cavaliers': 1610612739,
                'Dallas Mavericks': 1610612742, 'Denver Nuggets': 1610612743, 'Detroit Pistons': 1610612765,
                'Golden State Warriors': 1610612744, 'Houston Rockets': 1610612745, 'Indiana Pacers': 1610612754,
                'Los Angeles Clippers': 1610612746, 'Los Angeles Lakers': 1610612747, 'Memphis Grizzlies': 1610612763,
                'Miami Heat': 1610612748, 'Milwaukee Bucks': 1610612749, 'Minnesota Timberwolves': 1610612750,
                'New Orleans Pelicans': 1610612740, 'New York Knicks': 1610612752, 'Oklahoma City Thunder': 1610612760,
                'Orlando Magic': 1610612753, 'Philadelphia 76ers': 1610612755, 'Phoenix Suns': 1610612756,
                'Portland Trail Blazers': 1610612757, 'Sacramento Kings': 1610612758, 'San Antonio Spurs': 1610612759,
                'Toronto Raptors': 1610612761, 'Utah Jazz': 1610612762, 'Washington Wizards': 1610612764}
    
    conn = pg2.connect(dbname= "wins_contr", host = "localhost")
    cur = conn.cursor()

    for team_name, team_id in team_ids.items():
        team_projection = """SELECT player_id, player_name, final_wins_rounded, final_losses_rounded,
                                ROUND(final_player_wins::numeric,3) final_player_wins, ROUND(final_player_losses::numeric,3) final_player_losses
                        FROM player_projections_2020_updated
                        WHERE team_id = %(team_id)s
                        ORDER BY final_player_wins DESC
                        """

        projected_team_df = pd.read_sql(team_projection, con=conn, params={'team_id': team_id})

        wins_df = projected_team_df.drop(columns='final_player_losses')
        losses_df = projected_team_df.drop(columns='final_player_wins')
        wins_df = projected_team_df.rename(columns={'final_player_wins':'wins_contr'})
        losses_df = projected_team_df.rename(columns={'final_player_losses':'wins_contr'})
        wins_df['win_loss'] = 'Win'
        losses_df['win_loss'] = 'Loss'

        projected_team_df = wins_df.append(losses_df)
        plt.figure(figsize=(10,8))
        sns.set_style("ticks")

        team_plot = sns.barplot(x="player_name", y="wins_contr", hue="win_loss", data=projected_team_df, palette={'Win':'#ffab00', 'Loss':'#4b86b4'}, saturation=.75, ci='sd')
        
        #plt.title(player_name_list[idx], fontsize=18)
        plt.ylabel('Total Contributed', fontsize=10)
        plt.xlabel('',fontsize=0)

        sns.despine(offset=10, trim=True)
        plt.xticks(rotation=35)
        save_name = team_name.lower().replace(' ', '_')
        print('Player Career: ', save_name)              
        filepath = '/Users/jacobpress/Projects/personal_website/static/images/wins_contr/team_projections/' + save_name
        plt.savefig(filepath)
        
        plt.close()

projected_team_graphs()