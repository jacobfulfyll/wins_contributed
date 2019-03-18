# Wins Contributed Full Calculation

Each game is treated as its own entity, with each team vying for the entirety of 1 point (win). This 1 point is divvied up between all of the players on the winning team based on the amount of calculated value they provide during that game. Below are the explicit details of the "value provided" calculation and how it becomes the Wins Contributed metric.

At its core, Wins Contributed is a box score statistic. To improve the metric, possession by possession data is analyzed to adjust classic box score statistics and achieve more accurate values. Unfortunately, possession by possession data is limited. When unavailable, Wins Contributed fills in the gaps with end of game box score information. After calculating these values, adjustments are made based on: team performance while a player was in the game and amount of time played by each player. All of this is explained in detail below.

## Possession Based Statistics:

Possession based scores use NBA textual play_by_play data. The scores take into account the actual result of a possession and assign value for each player who contributed to that outomce.

## Results Focused Value:

The goal of wins contributed is to estimate the amount of wins a player actually contributed to his team's win total within a given time period. To make this as accurate as possible, Wins Contributed evaluates players impact by looking at the end result of possessions. The statistics analyzed and adjusted on a possessional basis are:

1. Made_FG_Score
2. Missed_FG_Score
3. Ast_Score
4. Orebs_Score
5. Drebs_Score
6. TO_Score
7. Stls_Score
8. Blks_Score
9. FT_Score 
10. Def_Fouls_Score

## Possession Nuances

1. Assists to three pointers are worth proportionally more than assists on two pointers
2. Offensive rebounds are only rewarded when the team scores following the rebound, and are rewarded proportionally more when they come before a three versus a two
3. Blocks are only rewarded when the team gets a stop following the block
4. Defensive Fouls can result in positive or negative value depending on how many free throws the opponent makes
5. If a player misses a shot which is followed by an offensive rebound and score, the player who missed the shot is not penalized

## How Possession Scores Are Calculated

#### Calculate The Value Of A Possession 
  - **Winning Team Possession Value =** *Winning Team Total Points Scored / Winning Team Total Possessions*
  -**Losing Team Possession Value =** *Losing Team Total Points Scored / Losing Team Total Possessions*

#### Analyze The Outcome Of Possessions
*Offensive Possessions*
  - If a possession results in a **Made Basket,**  the value of that basket is determined using the below formula:
    - **Offensive Value Created** = *Points Scored On Possession - Winning Team Possession Value*
    - For each possession where value is created, Wins Contributed assigns a percentage of that value to each player who had a hand in the basket. The percentage structures which govern how much value a specific stat receives are shown below:
      - *Made_FG Value Structure:*
        - **100%** of value awarded when basket is unassisted and not following an offensive rebound
        - **70%** of value awarded when basket is assisted and not following an offensive rebound
        - **50%** of value awarded when basket is unassisted and following an offensive rebound
        - **40%** of value awarded when basket is assisted and following an offensive rebound
      - *Offensive Rebounding Value Structure:*
        - **50%** of value is awarded if there is no assist on the basket
        - **40%** of value is awarded if there is an assist on the basket
        - **Note** This value is divvied up evenly between the offensive rebounders if there are multiple offensive rebounds within one possession
      - *Assists Value Structure:*
        - **30%** of value is awarded if there is no offensive rebound on the given possession
        - **20%** of value is awarded if there is an offensive rebound on the given possession
  - If a possession results in a **Missed Basket or Turnover** value lost is calculated as:
    - **Value Lost =** *(Negative) Winning Team's Possession Value For Total Game*
    - *Missed FG* deduct **100%** *Value Lost* from a players score 
      -If a player missed a shot which is followed by an offensive rebound and a score, the player is not deducted anything for missing that shot.
    - *Turnovers* deduct **100%** *Value Lost* from a players score

*Defensive Possessions*
  - Defensive stats in the NBA are harder to come by, especially on a possession by possession basis. We are still able to calculate blocks, steal, and defensive rebounds on a possessional basis.
  - If a possession results in a **Made Basket** unfortunately there is no good way, by possession or by game, to assign negative values to the players responsible. 
  - If possession results in a **Missed Basket or Turnover** the players involved are rewarded with value created from the defensive stop:
    - **Defensive Value Created =** *Losing Team's Possession Value For Total Game*
      - *Blocks Value Structure:*
        - **100%** of value awarded when the block is followed by an unattributable team rebound
        - **90%** of value awarded when the block is followed by a defensive rebound
        - **50%** of value awarded when the block is followed by a recovery by the losing team and a subsequent turnover later in the possession
      - *Steals Value Structure:*
        - **100%** of value awarded when the steal is the only notable aspect of the defensive possession
        - **50%** of value awarded when the steal is preceded by a block earlier in the possession
      - *Defensive Rebounds Structure:*
        - **20%** of value awarded when there is nothing notable in the play by play except for a missed shot
        - **10%** of value awarded when the defensive rebound is preceded by a block, before a change in possession

*Free Throw Possessions*
  - These values can be positive or negative. They depend on the amount of free throws made and value of the possession
  - Stats like blocks and offensive rebounds also take free throws into account to determine their value
  - **FT_Score Value Created =** *Free Throws Made On Possession - Winning Team's Possession Value For Total Game*
  - **Def_Fouls_Score Value Created =** *Losing Team's Possession Value For Total Game - Free Throws Made On Possession*
  - From that calculation we apply the value structures similar to all the other stats
    - *FT_Score Value Structure:*
      - **70%** of value *awarded* when basket before free throw is assisted
      - **50%** of value *awarded* when there was an offensive rebound before the free throws
      - **40%** of value *awarded* when there was an offensive rebound and an assist before
      - **100%** of value is *deducted* if the possession points are less than the expected value of a possession 
    - *Def_Fouls_Score Value Structure:*
      - **100%** of value is *awarded* when there was no block preceding and the actual points scored on the possession was less than the expected value of the possession.
      - **10%** of value is *awarded* when there was a block preceding and the actual points scored on the possession was less than the expected value of the possession.
      - **100** of value is *deducted* when the points scored on the possession was greater than the expected value of the possession.

## Game Based Statistics:

The following statistics are calculated on a game by game basis:

1. DFG_Score
2. Sast_Score
3. FT_Ast_Score

#### Game Statistics Calculations

- **Defensed Field Goals =** *Defended Field Goals Attempted - Defended Field Goals Made*

- **DFG_Score =** *Defensed Field Goals x Losing Team Possession Value x .8*
  - Defended Field Goals receive 80% of value created from the defensive stop

- **Sast_Score** = *Screen Assists x Winning Team Possession Value x .3*

- **FT_Ast Score** = *Free Throw Assists X Winning Team Possession Value x .3*
  - Both above metrics are multiplied by .3, per the assists value structure

## Factoring In Offensive and Defensive Rating

After calculating the value scores for the box score stats, Wins Contributed then makes adjustemtns using offensive and defensive rating. These ratings judge how well a team played with that player on the floor. If players have positive ratings, their scores are adjusted proportionally higher and vice versa.

#### Offensive and Defensive Rating Calculations

- **Player Offensive Rating** - The amount of points the team scores per 100 possessions while a specific player is on the floor
- **Team Offensive Rating** - The amount of points the team scores per 100 possessions
- **Player Defensive Rating** - The amount of points the team surrenders per 100 possessions while a specific player is on the floor
- **Team Defensive Rating** - The amount of points the team surrenders per 100 possessions

#### Offensive and Defensive Factor Calculations

- **Offensive Factor =** *Player Offensive Rating / Team Offensive Rating*
- **Defensive Factor =** *Player Defensive Rating / Team Defensive Rating*

## Box Score Output

Below is an example output of all the stats we calculated thusfar. The Game Value Score in the second most right column is the sum of all columns ending in _Score. To get from Game Value to wins contributed, a couple more adjustments must be made.

| Player           | Made_FG_Score | Ast_Score | Orebs_Score | Drebs_Score | TO_Score | Stls_Score | Blks_Score |  FT_Score | DFG_Score | Sast_Score | FT_Ast_score | Missed_FG_score | Def_Fouls_Score | Game_Value  | Wins_Contributed |
|:----------------:|:---------:|:---------:|:-----------:|:-----------:|:--------:|:----------:|:------------:|:---------:|:---------:|:----------:|:------------:|:---------------:|:---------------:|:-----------:|:----------:|
|Jayson Tatum      | 10.6      | 1.73      | 1.16        | 1.19        | -0.74    |   0.85     |            0 |     1.76  |         0 |   0.45     |            0 |        -4.47    |        0.67     |      13.23  |    0.247   |
|Gordon Hayward    | 3.29      | 0         | 0.60        | 0.48        |  0       |   3.22     |            0 |    -1.13  |   1.20    |   0.41     |            0 |        -4.24    |       -0.22     |      3.63   |    0.109   |
|Al Horford        | 3.13      | 0.97      | 0           | 0.59        | -2.65    |   0        |      5.034   |   0.072   |   5.59    |          0 |     0.16     |        -2.65    |       -0.23     |      10.02  |    0.214   |
|Jaylen Brown      | 4.43      | 0.87      | 0           | 0.27        | -1.96    |   0        |            0 |    0.11   |         0 |   0.35     |            0 |        -7.85    |        0.84     |     -2.92   |   0.046    |
|Kyrie Irving      | 2.17      | 3.11      | 0           | 0.55        | -2.77    |   0        |            0 |     1.28  |         0 |   0.37     |            0 |        -10.1    |        -1.34    |     -6.76   |           0|
|Marcus Morris     | 6.87      | 0         | 0.68        | 0.95        | -0.95    |   1.19     |            0 |          0|         0 |          0 |            0 |        -4.77    |        -3.93    |    0.047    |   0.059    |
|Terry Rozier      | 5.86      | 0.31      | 0           | 1.43        | -0.94    |   0        |      1.67    |          0|   1.33    |   0.37     |            0 |        -4.72    |        0.63     |      5.96   |    0.144   |
|Marcus Smart      | 2.69      | 1.50      | 0           | 0.48        | -1.50    |   0        |            0 |    0.14   |         0 |          0 |            0 |       -0.75     |        -1.17    |      1.39   |   0.087    |
|Aron Baynes       | 3.71      | 1.38      | 0.86        | 0.15        | -0.89    |   0        |            0 |       0   |   1.16    |          0 |            0 |        -3.58    |        -1.21    |      1.57   |   0.068    |
|Daniel Theis      | 0         | 0         | 0           | 0.17        |  0       |   0        |            0 |       0   |         0 |          0 |            0 |               0 |        -1.05    |     -0.87   |   0.010    |
|Semi Ojeleye      | 0         | 0         | 0           | 0.30        |  0       |   0        |            0 |       0   |         0 |          0 |            0 |               0 |               0 |     0.30    |  0.004     |
|Guerschon Yabusele| 0         | 0         | 0           | 0           |  0       |   0        |            0 |       0   |         0 |          0 |            0 |               0 |               0 |            0|  0.004     |
|Brad Wanamaker    | 1.10      | 0         | 0           | 0.30        |  0       |   0        |            0 |       0   |         0 |          0 |            0 |               0 |               0 |      1.40   |   0.002    |

## Negative Value Adjustment

Since players receive negative points for poor actions on the court, negative numbers can throw off the Wins Contributed calculation. To fix this, the player with the lowest Game Value Score is pegged to the value 0, and each of the other player's scores are adjusted accordingly. This only applies to players who actually played. The example below references the previously shown table.

  - Kyrie Irving had the lowest Game Value Score, -6.76
  - Jayson Tatum had the highest Game Value Score, 13.23
  - To normalize these values we make Kyrie Irving's score 0 and Jayson Tatum's score 19.99 (13.23 + 6.76)
  - This means that the Kyrie Irving will receive 0 Wins Contributed for this win
    - This example specifically picks out an issue with this metric, where the player who contributed the least on the team according to Game Value is not awarded any Win Shares. Often times this can be the best player on the team who may be having a bad game because they have the ball most and can take the most actions on the court.

  - **Normalized Game Value Score =** *Specific Player Game Value Score - Lowest Player Game Value Score*

After determining the Normalized Game Value Score we determine how much of the Game Value was contributed by each player on the team:
  - **Game Value Contributed =** *Specific Player Normalized Game Value Score / Sum of All Players Normalized Game Value Scores*


## Playing Time Adjustment
Because Wins Contributed considers both positive and negative impacts it is important to give more credit to those who play more. It is a lot easier to go one for one from the field and provide positive value than it is to take 20 shots and provide positive value. 

  - A superstar having a bad game may miss many shots resulting in slightly less value provided in the aggregate metric, but provide much more to the win in reality.
  - To fix this we perform one more adjustment to get a final value provided for each player
    - Playing Time Adjustments = Seconds Played / (Total Seconds In Game * 5)
      - Total seconds in a game is multiplied by 5 to account for all 5 players on the floor

  - **Percent of Game Played =** *Seconds Played By Specific Player / (Total Seconds In A Game * 5)*


## Wins Contributed

  **Final Value =** *Game Value Contributed * Percent of Game Played*

  **Wins Contributed =** *Final Value / Sum of Final Values