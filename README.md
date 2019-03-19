# NBA Wins Contributed Statistic 

In every sport determining which player reigns supreme is on the forefront of fans minds. In no sport is this more prevelant than basketball. Debates constantly rage about who the greatest player of all time is, who should be MVP this year, and who the best player in the world is right now. Due to many moving pieces within the game, the different ways players provide value, and the difference in team compositions value in the NBA is difficult to quantify and makes these debates very subjective. Take this years MVP race, five of the current MVP front runners Giannis Antetokounmpo, James Harden, Kevin Durant, Paul George, and Nikola Jokic highlight five characteristics people usually attribute to MVP. 

1. **Giannis Antetokounmpo** - The best player on the best team in the league.
2. **James Harden** - The player doing everything for their team.
3. **Kevin Durant** - The best player in the world. Usually this is Lebron James (IMO).
4. **Paul George** - The best two-way (combined offensive and defensive) player.
5. **Nikola Jokic** - The feel-good, surprise contender, with actual skill

As a result of basketball's intricacies, many stats exist to rank the best individual players in the league. These stats like Player Efficiency Rating (PER), Player Impact Estimate (PIE), Win Shares, Value Over Replacement Player (VORP), and Box Score Plus/Minus (BPM) all present unique ways to evaluate talent. With all of the advanced metrics out there and computing never more powerful, there are surprisingly few advanced metrics that place an emphasis on winning, game by game analysis, possession by possession outcomes, team composition, and durability.

# Introducing Wins Contributed

Wins contributed measures players contribution in every win. By doing this, we can graph the MVP race for any given year game by game. Below is a video showing the MVP race using Wins contributed for games 119 through 1023 in the 2018-2019 regular season. If you would like to see the full video, videos for other years, and plenty of other graphs describing previous NBA Seasons, [click here](https://github.com/jacobfulfyll/wins_contributed/tree/master/Graphs):

![Alt Text](Graphs/MVP_Races/2018-19.gif)


## How is this calculated? 

By making each game a seperate entity with a definitive outcome, Wins Contributed aims to show how many wins a player contributes to his team over the course of any given time period. It is calculated on a game by game basis using 6 distinct steps. A summary of the steps is provided below, but if you're looking for a complete calculation, [click here](https://github.com/jacobfulfyll/wins_contributed/blob/master/fullCalculation.md)

  1. **Determine Which Team Won The Game**
    - In Wins Contributed only players on the winning team receive value
    - Each win is worth 1 point and that 1 point is divided between each of the players on the winning team, based on their value provided in that game
  2. **Assign Value To Each Player**
    - Wins Contributed analyzes each possession in a game and awards players points based on the outcome of each possession. Below are two examples of the many adjustments made to typical box score stats using possessional data 
      - If a player grabs an offensive rebound, but the team can't turn that rebound into points, the offensive rebound is deemed worthless.
      - An assist on a three pointer is worth more than an assist on a two pointer
    - Value is determined on a game by game basis
      - Offensive Value = Points Scored On Given A Possession - Value Of A Possession For The Winning Team
      - Defensive Value = Value Of A Possession For The Losing Team
      - Value Of A Possession For The Winning Team = Winning Team Points Scored / Winning Team Total Possessions
      -  Value Of A Possession For The Losing Team = Losing Team Points Scored / Losing Team Total Possessions
        - Value of possessions for each team is calculated on a game by game basis. This is unlike most advanced metrics which take into account teams seasonal performances. I think this provides an interesting way to look at actual match ups, not shown by average data.
  3. **Normalize Value To Reality**
    - Box score stats are great, but they also have their limitations. To make up for some of these limitations the value determined through the box score stats is normalized using offensive and defensive ratings.
      - Offensive and Defensive Ratings measure how many points were scored/surrendered for a given player or the entire team per 100 possessions
    - Wins Contributed calculates an offensive and defensive factor for each player for each game
      - Player Offensive Factor = Player Offensive Rating / Team Offensive Rating
      - Player Defensive Factor = Player Defensive Rating / Team Defensive Rating
    - Offensive/Defensive Factors above 1 increase a players value for every Offensive/Defensive statistic because the team was playing better than average while they were on the floor
    - Factors below 1 decrease players value for the opposite reason
  4. **Negative Values Adjustments**
    - Final values contributed from the box score statistics and ratings factor for a player can be negative. This creates an issue when trying to assign each player a percentage of the win.
    - To fix this, Wins Contibuted sets the player with the lowest value at the end of the game to 0 and calculates all other values using them as a baseline.
      - If the lowest value for a player was -6 and the second lowest was -4, the -6 value is set to 0 and the -4 value is set to 2
      - This means the player who contributed the least calculated value in every win is given 0 Wins Contributed
  5. **Playing Time Adjustments**
    - Because Wins Contributed considers both positive and negative impacts it is important to give more credit to those who play more. It is a lot easier to go one for one from the field and provide positive value than it is to take 20 shots and provide positive value. 
    - A superstar having a bad game may miss many shots resulting in slightly less value provided in the aggregate metric, but provide much more to the win in reality.
    - To fix this we perform one more adjustment to get a final value provided for each player
      - Playing Time Adjustments = Seconds Played / (Total Seconds In Game * 5)
        - Total seconds in a game is multiplied by 5 to account for all 5 players on the floor
  6. **Calculate Wins Contributed**
    - Now we have a fair value for how much each player has contributed to this win
    - Wins Contributed = Player Value / Sum Of All Player Values
      - The wins each player contributes in a given game is their percentage of the total value in the game.

# What good is this?

**Unlike many other stats, Wins Contributed does not purely value efficiency, team performance, or counting specific metrics, rather it attempts to blend all three.**
  - From an efficiency perspective it rewards players for their contributions, penalizes them for their failings and relates it all to the value of a possession in the associated game. 
  - It values team performance above all because you only receive points when your team wins. It also incorporates team performance by factoring in the how the team performs while each player is on the floor. 
  - Finally it values counting stats although not in a typical way. Wins contributed turns most of the typical counting stats into efficiency based metrics, but values longevity and durability by counting the amount of wins players contribute. By doing this it gives credit to players who have had successful NBA careers on great teams, but may have been overlooked for one reason or another. It points out who actually does what matters most in basketball and all sports, win the game.

### League and Team Scatter Plots
Creating scatter plots with the sum of a player's wins contributed and their average wins contributed per win shows both who contributes the most in a single win and who has contributed the most to wins in total. Additonally, next to players name is a number which represents their max win contribution for any single game on the entire season. This gives us an idea of who has the capacity to contribute in a big way, even if they don't do it consistently yet. Below is the 2018-19 Season. 15 players have been labeled, 10 with the highest wins for a single game and 5 randomly generated.

![Alt Text](Graphs/Season_Scatters/2018-19.png)

This also allows us to see team contributions in from a new perspective. Below you'll see the contributions for each player on the Los Angeles Lakers and Golden State Warriors:

![Alt Text](Graphs/Team_Scatters/2018-19/Lakers.png) ![Alt Text](Graphs/Team_Scatters/2018-19/Warriors.png)

### Insight Still To Come
1. **Nightly Best Players Tool**:
    - Because Wins Contributed is calculated on a per game basis it can provide a nightly look at players who contributed the most to their team in any given night. 
2. **Career Arc Comparison**:
    - At the end of the day it values wins and compares each player to their teammates. Because of this, it has the unique ability to compare players across generations throughout different points in their career. 
3. **Contract Value Contributions**:
    - With wins being correlated to team's financial success, pegging wins contributed to the amount of dollars earned for each player gives insight into which players are the most under and over paid.
4. **Regular Season vs Playoffs**:
    - Everyone who watches the NBA knows regular season success doeesn't always translate to playoff success. Win's contributed provides a way to compare how players skillsets transition from the grind of the regular season to the competitiveness of the playoffs.
5. **Value Contributed In Losses**:
    - Which players contribute a lot of value in losses. Is there a differen in how some players perform in losses compared with wins? Finding out the value players contirbute in losses can give us a fuller picture of value through Wins Contributed.

# What Are The Flaws

No stat is perfect, so what are the flaws in Wins Contributed?

1. *Inadequacy in valuing defense, especially perimeter defense:*
    - Wins Contributed gives credit for steals, blocks, and defended field goals, but can't adequately measure "individually bad defense." This is challenging for all basketball stats, so I was okay making a concession in this area.
2. *Evaluating players compared to teammates on a game by game basis:*
    - I believe this can be seen as a weakness, but was also something I wanted to be in the stat. Playing basketball myself, I'm biased towards believing players have on days and off days, so at least one stat should evaluate players on a game by game basis. However, this runs the risk of penalizing or rewarding players based on luck by looking at outcomes on such a small sample size. I do believe over the long run you will get interesting aggregate information that may differ from the agreggate information collected on a seasonal basis and it will hopefully be more true to reality, luck included.
3. *0 Wins For The Worst Player:*
    - Because it evaluates most of the metrics on efficiency and deems that the player with the lowest value provided at the end of the game earns 0 Wins Contributed, superstars having bad games will sometimes end up with duds. They make and miss more shots than players with smaller roles and have the ball more to do both great and terrible things on the court. 
4. *Arbitrary Percentages For Value Contributions:* 
    - This is easy when there is only one person responsible for a positive or negative outcome. If James Harden turns the ball over, he loses the entire value of that possession, if he hits an unassisted shot that wasn't preceded by an offensive rebound he received the entire value of the points he created minus the value of a possession. When multiple players are involved, each player receives or loses a percentage of that value created or lost. The big flaw is that those percentages are fixed and although seemingly logical, they are arbitrary. Eventually the goal is to complete more sophisticated modeling to test various percentage splits to come up with percentages that best reflect reality.
5. *Lack of Fringe Statistics:* 
    - Wins Contributed does not consider some fringe intangible statistics, things like loose balls, boxouts, and deflections which certainly provide value towards winning basketball games. I hope to add these by the beginning of the 2019-2020 season.

# 2016 - 2019 Cumulative Wins Contributed

The below table shows the cumulative Wins Contributed for every player from 2016 - 2019. Before the start of next season, I want to add every NBA season possible to find out who the regular season Wins Contibuted GOAT is!

Rank| player_name        | pts_score | miss_score | ft_score | ast_score | ft_ast | sast_score | orebs_score | drebs_score | to_score | stl_score | blk_score | dfg_score | pf_score | total_score |  wins
--|------------------------+-----------+------------+----------+-----------+--------+------------+-------------+-------------+----------+-----------+-----------+-----------+----------+-------------+--------
1| James Harden             |  1723.353 |  -1288.819 |  528.268 |   541.339 |  7.827 |     40.614 |      31.219 |     174.252 | -785.366 |   268.590 |    69.899 |   104.873 |  130.171 |    1551.653 | 39.866
2|Giannis Antetokounmpo    |   997.162 |   -710.854 | -120.601 |   314.560 |  2.469 |     29.802 |      76.356 |     213.461 | -409.024 |   188.912 |   158.971 |   178.159 |  102.017 |    1022.672 | 29.923
3| LeBron James             |  1247.260 |   -822.965 | -168.466 |   472.422 |  5.945 |     36.413 |      45.199 |     186.322 | -498.016 |   168.017 |    57.245 |   128.304 |   52.791 |     913.720 | 29.184
4| Kevin Durant             |  1181.893 |   -955.105 |  180.451 |   305.604 |  2.950 |     30.490 |      20.153 |     187.699 | -426.884 |   122.416 |   156.798 |   156.049 |    0.210 |     964.496 | 28.919
5|  Stephen Curry            |  1405.888 |  -1074.822 |  232.651 |   314.499 |  5.844 |     58.024 |      29.206 |     116.184 | -455.417 |   225.105 |    20.408 |    46.017 |   18.908 |     944.026 | 27.884
6| Paul George              |  1134.854 |   -892.103 |  174.275 |   177.714 |  3.717 |     18.076 |      29.691 |     140.922 | -333.579 |   239.750 |    43.699 |   116.994 |   79.468 |     935.595 | 27.548
7| Damian Lillard           |  1168.343 |   -895.424 |  330.317 |   293.757 |  6.086 |     28.406 |      25.084 |      89.077 | -309.354 |   126.825 |    36.441 |    51.411 |    2.882 |     956.752 | 26.960
8| Russell Westbrook        |  1226.005 |  -1054.226 |   47.504 |   538.400 |  8.538 |     31.137 |      55.218 |     227.013 | -637.666 |   224.766 |    26.780 |    71.862 |  134.763 |     903.211 | 26.615
9| Rudy Gobert              |   430.809 |   -219.571 | -200.571 |    78.876 |  1.144 |     10.021 |     105.968 |     212.370 | -227.605 |    87.490 |   229.018 |   337.375 |   77.945 |     923.372 | 26.417
10| Nikola Jokic             |   703.897 |   -517.870 |   36.072 |   307.424 |  3.721 |     18.482 |      96.018 |     200.541 | -346.002 |   143.567 |    62.315 |   215.623 |  119.304 |    1044.381 | 26.350
11| Chris Paul               |   841.697 |   -634.873 |  141.864 |   413.655 |  6.835 |     30.292 |      22.172 |     109.222 | -300.599 |   230.850 |    19.961 |    65.317 |   66.422 |    1014.762 | 25.896
12| Jimmy Butler             |   696.739 |   -522.956 |  174.015 |   207.024 |  2.857 |     16.724 |      46.837 |      87.633 | -189.359 |   215.717 |    37.198 |    91.264 |   33.472 |     898.382 | 25.783
13| Kyle Lowry               |   902.822 |   -657.380 |   80.521 |   361.352 |  6.916 |     29.533 |      22.568 |     113.021 | -350.422 |   161.876 |    26.298 |    72.411 |   60.890 |     833.319 | 25.263
14| Draymond Green           |   449.721 |   -490.699 |  -42.138 |   397.889 |  5.036 |     32.946 |      35.848 |     186.778 | -392.528 |   232.533 |   136.577 |   241.834 |   79.821 |     875.827 | 25.106
15| Karl-Anthony Towns       |   756.007 |   -576.438 |   69.445 |   107.969 |  1.202 |     12.853 |     107.435 |     197.839 | -279.705 |    90.059 |   117.333 |   210.000 |   76.857 |     891.715 | 24.393
16| Kyrie Irving             |  1111.767 |   -820.641 |  145.531 |   287.203 |  3.963 |     28.729 |      23.128 |      71.636 | -314.272 |   149.071 |    25.981 |    50.080 |   40.177 |     803.041 | 23.961
17| Anthony Davis            |   795.081 |   -745.871 |   78.436 |   111.867 |  0.819 |      9.854 |      83.723 |     184.287 | -230.757 |   148.158 |   188.140 |   189.130 |   13.749 |     827.333 | 23.275
18| DeMar DeRozan            |  1125.362 |   -966.327 |   96.939 |   295.288 |  2.829 |     30.917 |      29.170 |     112.084 | -329.128 |   136.119 |    27.067 |    47.535 |   45.731 |     653.879 | 22.997
19| CJ McCollum              |  1137.293 |   -840.776 |   82.187 |   172.559 |  3.803 |     24.834 |      22.688 |      77.536 | -209.006 |   120.296 |    40.109 |    59.303 |   19.069 |     711.139 | 22.712
20| Al Horford               |   617.052 |   -521.005 |    2.090 |   238.341 |  3.163 |     17.569 |      49.359 |     136.996 | -225.919 |    84.308 |   114.523 |   189.185 |    5.054 |     711.901 | 21.401
21| LaMarcus Aldridge        |   854.984 |   -865.653 |   66.526 |   129.008 |  1.582 |     17.522 |     102.896 |     134.995 | -237.450 |    76.829 |   120.878 |   177.695 |   16.410 |     596.345 | 20.795
22| Bradley Beal             |   999.864 |   -772.288 |   82.447 |   213.234 |  3.326 |     37.326 |      27.200 |      75.475 | -302.948 |   143.323 |    37.209 |    65.227 |   14.465 |     625.501 | 20.709
23| Klay Thompson            |  1317.274 |  -1174.297 |   66.472 |   130.496 |  4.484 |     30.284 |      24.949 |     100.420 | -288.455 |   126.583 |    65.062 |   111.692 |   15.712 |     532.122 | 20.427
24| Clint Capela             |   531.995 |   -266.891 | -223.221 |    62.399 |  0.975 |     11.638 |     121.905 |     193.459 | -195.997 |    89.973 |   156.392 |   273.913 |   83.275 |     839.968 | 20.023
25| Tobias Harris            |   830.770 |   -614.859 |   44.871 |   115.365 |  1.215 |     15.804 |      29.618 |     124.541 | -166.398 |    86.417 |    38.922 |   119.793 |    2.343 |     629.085 | 19.833
26| Kemba Walker             |   921.537 |   -708.387 |  153.633 |   227.935 |  4.268 |     29.714 |      16.460 |      59.377 | -233.280 |   112.719 |    25.376 |    45.981 |   -7.032 |     649.624 | 19.784
27| Kawhi Leonard            |   787.212 |   -650.703 |  133.858 |   132.621 |  1.803 |     16.217 |      35.996 |      89.946 | -182.084 |   162.767 |    37.854 |    50.844 |   15.416 |     631.730 | 19.529
28| Steven Adams             |   503.779 |   -322.313 | -147.003 |    67.343 |  0.564 |      7.481 |     138.307 |     105.289 | -218.215 |   169.058 |    90.999 |   205.428 |   82.311 |     683.303 | 19.343
29| Victor Oladipo           |   839.333 |   -617.392 |   25.291 |   171.753 |  2.282 |     15.202 |      17.633 |      97.811 | -264.297 |   204.881 |    33.503 |    75.229 |   26.779 |     631.267 | 19.274
30| Andre Drummond           |   473.328 |   -386.632 | -215.822 |    71.618 |  0.465 |      4.285 |     121.140 |     215.050 | -225.037 |   156.031 |   126.099 |   191.197 |  118.449 |     650.825 | 18.778
31| Otto Porter Jr.          |   611.747 |   -467.465 |   17.783 |    77.968 |  1.124 |      7.843 |      39.685 |     114.600 | -101.138 |   159.944 |    55.639 |    86.493 |   10.997 |     615.803 | 18.165
32| Thaddeus Young           |   560.024 |   -473.914 |  -65.925 |   102.000 |  2.990 |      9.948 |      72.540 |     104.675 | -166.053 |   219.072 |    48.453 |    95.596 |   41.496 |     551.609 | 18.043
33| DeAndre Jordan           |   331.420 |   -181.963 | -216.469 |    62.013 |  1.231 |      3.990 |     104.131 |     233.503 | -181.785 |    76.269 |   106.601 |   141.344 |   75.058 |     555.861 | 17.957
34| Jrue Holiday             |   807.168 |   -630.286 |  -14.843 |   293.341 |  4.412 |     24.894 |      21.651 |      75.535 | -302.364 |   183.425 |    59.935 |    57.768 |  -12.076 |     571.226 | 17.683
35| Myles Turner             |   507.298 |   -487.602 |  -40.000 |    73.653 |  0.683 |      4.514 |      47.329 |     129.950 | -159.020 |    82.348 |   199.018 |   287.754 |   -5.380 |     640.657 | 17.671
36| Jeff Teague              |   556.575 |   -459.488 |  121.466 |   312.367 |  5.013 |     22.819 |       9.813 |      63.260 | -271.362 |   138.640 |    27.562 |    53.150 |   13.770 |     597.235 | 17.523
37| Blake Griffin            |   767.102 |   -594.503 |  -26.815 |   227.791 |  1.159 |     13.673 |      40.922 |     125.181 | -272.396 |    75.667 |    27.616 |   100.524 |   46.561 |     532.580 | 17.376
38| Trevor Ariza             |   583.614 |   -524.362 |    2.232 |   115.007 |  1.295 |     12.583 |      20.869 |     111.500 | -112.543 |   190.569 |    22.789 |    65.173 |   58.241 |     547.638 | 17.308
39| Joe Ingles               |   640.246 |   -422.217 |    0.763 |   218.931 |  4.926 |     24.703 |       8.526 |      84.771 | -259.492 |   158.184 |    21.407 |    39.936 |   39.587 |     563.582 | 17.279
40| Serge Ibaka              |   630.293 |   -543.161 |   10.264 |    62.024 |  0.604 |     13.553 |      56.109 |     144.215 | -186.304 |    61.157 |   126.135 |   214.774 |   16.525 |     606.197 | 17.241
41| Khris Middleton          |   745.391 |   -633.161 |  119.837 |   159.176 |  2.275 |     13.578 |      11.879 |     102.311 | -265.367 |   129.308 |    16.773 |    44.613 |   46.715 |     495.003 | 16.834
42| Ben Simmons              |   501.474 |   -322.920 | -146.933 |   313.097 |  2.800 |     24.731 |      47.033 |     118.448 | -314.484 |   138.415 |    56.713 |    62.979 |   46.817 |     531.363 | 16.800
43| Darren Collison          |   502.298 |   -352.973 |   63.107 |   245.296 |  2.980 |     23.496 |      15.021 |      45.137 | -169.049 |   132.417 |    14.823 |    28.723 |   32.843 |     585.354 | 16.457
44| Joel Embiid              |   642.558 |   -569.654 |   14.878 |   113.957 |  0.732 |     10.159 |      63.333 |     169.110 | -315.509 |    70.990 |   136.376 |   242.749 |   33.532 |     614.284 | 16.394
45| Marc Gasol               |   541.842 |   -489.001 |   49.745 |   152.086 |  2.272 |      9.928 |      24.679 |     112.343 | -201.370 |    87.092 |    83.064 |   148.615 |   17.062 |     539.276 | 16.209
46| Eric Bledsoe             |   693.748 |   -573.574 |   39.715 |   228.166 |  4.691 |     22.448 |      25.288 |      79.250 | -285.190 |   157.371 |    39.948 |    60.075 |   50.540 |     544.280 | 15.805
47| Josh Richardson          |   513.310 |   -432.585 |   39.379 |   133.721 |  0.609 |     14.129 |      18.869 |      58.391 | -135.870 |   113.434 |    56.908 |    68.347 |   10.680 |     460.109 | 15.503
48| Danny Green              |   489.909 |   -395.630 |   17.861 |    79.896 |  1.274 |     12.644 |      20.820 |      79.834 | -137.108 |   127.180 |    93.192 |   101.748 |   18.174 |     510.364 | 15.412
49| PJ Tucker                |   388.400 |   -340.256 |   -5.284 |    62.063 |  0.539 |      7.003 |      45.309 |     124.970 | -123.828 |   177.713 |    35.568 |    96.051 |   44.282 |     513.029 | 15.244
50| Taj Gibson               |   438.122 |   -261.946 |   -8.559 |    46.366 |  1.000 |      7.585 |      69.574 |     110.149 | -137.282 |    82.033 |    52.905 |   114.629 |   40.408 |     555.564 | 15.120
51| Paul Millsap             |   514.991 |   -438.384 |  -16.125 |   125.716 |  2.416 |     10.259 |      48.672 |     110.289 | -198.593 |   132.160 |    74.286 |   150.490 |    4.759 |     521.423 | 14.963
52| Dennis Schroder          |   755.745 |   -528.335 |   57.749 |   222.848 |  4.322 |     19.709 |       6.486 |      55.345 | -295.125 |    91.893 |     9.263 |    42.625 |   19.621 |     462.368 | 14.855
53| Mike Conley              |   559.934 |   -424.091 |   83.116 |   178.738 |  4.458 |     22.054 |       5.596 |      41.677 | -133.460 |    88.798 |     9.615 |    33.410 |   26.528 |     496.796 | 14.829
54| Jonas Valanciunas        |   491.139 |   -379.635 |    5.543 |    49.059 |  0.042 |      7.551 |      86.527 |     161.772 | -194.439 |    63.569 |    75.633 |   207.194 |   51.298 |     625.493 | 14.821
55| Lou Williams             |   789.264 |   -662.505 |  193.931 |   183.720 |  3.324 |     19.168 |      12.752 |      51.245 | -272.961 |   107.463 |    17.795 |    34.778 |   13.280 |     493.050 | 14.724
56| John Wall                |   649.583 |   -555.123 |   -3.871 |   334.698 |  5.048 |     26.102 |      11.512 |      50.646 | -329.328 |   141.773 |    49.224 |    58.043 |   18.092 |     457.482 | 14.621
57| JJ Redick                |   775.985 |   -705.641 |  172.736 |   115.317 |  1.632 |     21.753 |       7.199 |      61.810 | -169.009 |    66.838 |    13.397 |    32.627 |   34.583 |     429.978 | 14.555
58| Jamal Murray             |   700.173 |   -569.224 |  102.879 |   167.044 |  1.738 |     36.933 |      23.417 |      63.132 | -250.100 |   105.009 |    31.023 |    49.409 |   39.363 |     501.487 | 14.544
59| Robert Covington         |   452.717 |   -398.609 |   39.848 |    67.655 |  1.208 |      9.973 |      22.431 |      94.969 | -152.667 |   170.510 |    70.300 |    76.412 |  -22.820 |     432.586 | 14.310
60| Ricky Rubio              |   452.521 |   -437.586 |   77.013 |   272.143 |  4.608 |     27.809 |      12.660 |      75.784 | -264.700 |   146.567 |     9.789 |    37.592 |   56.594 |     473.057 | 14.268
61| Andre Iguodala           |   346.534 |   -279.651 |  -50.682 |   189.375 |  3.027 |     25.056 |      27.808 |      98.428 | -119.789 |   140.371 |    67.273 |    74.469 |    1.528 |     525.417 | 14.067
62| Hassan Whiteside         |   397.915 |   -333.461 | -103.317 |    35.914 |  0.216 |      1.690 |      93.882 |     158.734 | -151.295 |    64.621 |   142.820 |   185.062 |   15.652 |     508.607 | 13.987
63| Malcolm Brogdon          |   542.389 |   -400.251 |   68.837 |   158.025 |  3.885 |     16.303 |      17.813 |      65.281 | -169.442 |   101.721 |    14.268 |    57.289 |    1.353 |     478.629 | 13.884
64| Goran Dragic             |   627.357 |   -447.725 |   56.653 |   193.946 |  2.236 |     22.372 |      16.372 |      52.958 | -213.107 |    81.560 |    12.172 |    49.449 |   33.496 |     489.320 | 13.794
65| DeMarcus Cousins         |   535.973 |   -481.709 |  -25.988 |   133.687 |  1.380 |      8.053 |      40.844 |     127.631 | -268.030 |   103.068 |    66.150 |   125.221 |   83.578 |     451.005 | 13.735
66| Jae Crowder              |   562.403 |   -581.031 |   25.535 |    92.666 |  1.586 |      8.741 |      23.489 |     102.591 | -138.320 |   116.741 |    31.004 |    67.726 |   49.110 |     362.767 | 13.485
67| Jusuf Nurkic             |   477.789 |   -456.846 |  -81.811 |   107.976 |  1.760 |      2.948 |      79.521 |     152.891 | -281.558 |    92.382 |   121.222 |   229.161 |   74.752 |     521.255 | 13.433
68| Brook Lopez              |   552.075 |   -486.200 |   13.136 |    60.804 |  0.689 |      4.172 |      21.613 |      75.994 | -157.127 |    51.430 |   137.662 |   175.867 |   25.239 |     475.800 | 13.392
69| Patty Mills              |   605.559 |   -452.281 |   67.525 |   172.326 |  1.919 |     30.437 |      10.894 |      45.446 | -192.387 |   109.838 |     8.120 |    25.487 |   23.882 |     456.949 | 13.371
70| Cory Joseph              |   484.043 |   -384.481 |    1.026 |   210.589 |  1.500 |     24.881 |      18.486 |      75.296 | -172.330 |   125.441 |    23.503 |    53.995 |  -14.779 |     447.958 | 13.314
71| Bojan Bogdanovic         |   632.763 |   -460.149 |   69.144 |    69.546 |  0.627 |     12.054 |      11.766 |      69.443 | -172.131 |    73.679 |     5.931 |    54.338 |   40.798 |     408.216 | 13.251
72| Pascal Siakam            |   428.616 |   -347.276 |  -39.755 |   110.933 |  0.967 |     11.937 |      49.839 |     108.167 | -163.678 |   101.909 |    67.050 |   106.315 |   26.756 |     462.321 | 13.214
73| Terry Rozier             |   535.258 |   -446.226 |   20.677 |   152.917 |  1.388 |     23.017 |      20.694 |      95.366 | -120.887 |   119.664 |    21.606 |    37.644 |   26.482 |     488.340 | 13.191
74| Danilo Gallinari         |   436.140 |   -349.013 |  129.913 |    65.132 |  2.106 |      9.829 |      12.479 |      72.005 |  -90.208 |    52.296 |    22.036 |    61.056 |   16.969 |     441.055 | 13.050
75| Nicolas Batum            |   411.754 |   -405.527 |   31.160 |   177.620 |  3.211 |     16.323 |      20.600 |      89.197 | -186.023 |    98.240 |    27.809 |    56.062 |   39.394 |     381.214 | 12.904
76| Derrick Favors           |   401.378 |   -286.489 |  -83.930 |    63.073 |  0.860 |      4.721 |      82.880 |     106.217 | -129.697 |    90.100 |    81.356 |   185.394 |   -5.615 |     510.800 | 12.879
77| Marcus Smart             |   414.303 |   -476.543 |   25.264 |   241.366 |  2.855 |     19.466 |      24.345 |      63.577 | -258.788 |   200.766 |    32.950 |    60.852 |   -1.893 |     349.990 | 12.869
78| Marcus Morris            |   591.781 |   -503.687 |   34.778 |    70.141 |  1.016 |      8.616 |      36.988 |      96.046 | -124.193 |    62.469 |    22.253 |    61.682 |   39.695 |     397.567 | 12.799
79| Marcin Gortat            |   306.796 |   -283.386 |  -28.633 |    68.758 |  0.395 |     10.547 |      70.605 |     141.429 | -142.119 |    50.632 |    61.885 |   180.456 |   44.550 |     482.230 | 12.789
80| Will Barton              |   522.340 |   -367.837 |   16.670 |   130.981 |  0.571 |     13.290 |      19.547 |      70.295 | -168.876 |    66.098 |    32.339 |    54.958 |   18.563 |     409.481 | 12.681
81| Nikola Vucevic           |   452.271 |   -451.267 |  -12.756 |   102.093 |  1.275 |      5.832 |      48.751 |     119.344 | -117.541 |    75.592 |    61.461 |   148.291 |    5.246 |     439.097 | 12.680
82| Jayson Tatum             |   488.535 |   -412.090 |   66.255 |    63.319 |  0.165 |      8.280 |      15.254 |      84.484 | -139.061 |   100.287 |    48.464 |    58.914 |   22.731 |     405.810 | 12.623
83| Kelly Olynyk             |   476.613 |   -323.053 |   -7.024 |   113.811 |  1.371 |      6.975 |      35.862 |      94.755 | -185.345 |    82.784 |    40.906 |   122.747 |   15.003 |     475.538 | 12.556
84| Al-Farouq Aminu          |   351.729 |   -349.884 |   -7.626 |    53.649 |  1.135 |      6.332 |      41.045 |     136.276 | -123.050 |   110.278 |    49.409 |   111.763 |   27.390 |     408.740 | 12.488
85| Kentavious Caldwell-Pope |   490.170 |   -372.298 |   68.285 |    74.963 |  0.897 |     10.670 |      17.360 |      56.221 | -102.282 |   106.720 |     5.397 |    29.574 |   21.738 |     407.877 | 12.373
86| Gordon Hayward           |   523.605 |   -393.121 |   51.037 |   119.624 |  3.010 |     13.021 |      18.722 |      66.695 | -160.456 |    74.762 |    17.215 |    40.326 |   20.944 |     395.384 | 12.147
87| Isaiah Thomas            |   609.684 |   -471.697 |  157.117 |   148.856 |  2.341 |     22.822 |      12.952 |      25.654 | -195.375 |    52.253 |     8.073 |    14.587 |    8.488 |     396.122 | 11.883
88| T.J. McConnell           |   307.193 |   -226.988 |   -4.423 |   220.357 |  2.667 |     24.638 |      13.573 |      52.223 | -154.510 |   139.754 |    10.994 |    33.129 |   13.873 |     434.185 | 11.882
89| Marvin Williams          |   380.562 |   -300.756 |   15.385 |    47.802 |  0.578 |      5.641 |      26.950 |      85.637 |  -77.201 |    75.768 |    40.188 |    74.987 |   28.049 |     403.951 | 11.824
90| Julius Randle            |   468.993 |   -316.465 |  -56.456 |   124.401 |  1.253 |      9.798 |      49.545 |     109.443 | -221.555 |    56.224 |    37.533 |   102.407 |   60.470 |     425.986 | 11.785
91| Kevin Love               |   482.613 |   -487.559 |  109.502 |    54.262 |  0.419 |      9.905 |      42.275 |     142.486 | -165.448 |    63.185 |    19.498 |   113.150 |   19.019 |     403.639 | 11.759
92| Gary Harris              |   513.403 |   -409.700 |   13.049 |   100.810 |  1.064 |     12.876 |      16.586 |      44.670 | -147.030 |   130.742 |    20.100 |    28.851 |   39.436 |     365.022 | 11.663
93| Harrison Barnes          |   556.441 |   -546.954 |   72.306 |    63.121 |  0.812 |      6.755 |      24.156 |      69.050 | -114.247 |    50.619 |    10.709 |    48.979 |   27.894 |     269.757 | 11.660
94| Donovan Mitchell         |   713.635 |   -572.315 |    6.831 |   152.706 |  1.251 |     17.838 |      16.000 |      50.536 | -231.953 |   107.122 |    18.476 |    31.395 |   29.816 |     342.540 | 11.487
95| Patrick Beverley         |   332.159 |   -309.079 |  -12.396 |   146.530 |  2.770 |      9.848 |      29.457 |      73.896 | -139.560 |   113.520 |    26.041 |    49.542 |   58.199 |     381.119 | 11.467
96| Buddy Hield              |   547.319 |   -408.739 |   34.194 |    74.565 |  0.597 |      8.838 |      16.780 |      58.125 | -115.978 |    62.626 |    14.112 |    53.974 |   30.135 |     376.826 | 11.449
97| Kyle Anderson            |   201.402 |   -169.159 |  -18.817 |    99.883 |  0.712 |     13.085 |      23.078 |      76.774 |  -81.773 |   120.575 |    49.974 |    66.326 |   37.682 |     420.732 | 11.353
98| Markieff Morris          |   435.761 |   -407.802 |   38.585 |    62.428 |  1.395 |      6.324 |      36.393 |      93.050 | -170.202 |    96.017 |    34.453 |   113.777 |   49.280 |     390.120 | 11.327
99| James Johnson            |   417.206 |   -297.565 |  -38.017 |   160.376 |  2.092 |      8.117 |      16.254 |      75.171 | -169.166 |    93.100 |    79.228 |    66.587 |    3.112 |     418.049 | 11.303
100| Eric Gordon              |   898.516 |   -793.906 |   16.862 |   131.721 |  1.033 |     12.019 |      14.614 |      56.692 | -237.035 |    83.925 |    43.545 |    49.192 |   10.569 |     288.295 | 11.303

