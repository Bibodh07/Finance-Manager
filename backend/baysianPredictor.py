import pandas as pd 
import json 
from scipy.stats import zscore, norm





def baysianPredictorHome(team):
    df = pd.read_json("stats.json", orient="columns")
    df = df.T
    df_team = df.loc[team]

    if int(df_team.loc["total_wins"]) == 0:
        return 0.01

    # each factor calculated independently
    prior = int(df_team.loc["total_wins"]) / int(df_team.loc["games_played"])
    
    home_factor = int(df_team.loc["home_wins"]) / int(df_team.loc["home_games"]) if int(df_team.loc["home_games"]) > 0 else 0.5
    
    elo_factor = norm.cdf((int(df_team.loc["elo"]) - 1500) / 150)
    
    form_factor = int(df_team.loc["last_10_wins"]) / 10
    
    net_factor = norm.cdf(int(df_team.loc["avg_point_diff"]) / 5)

    # weighted sum
    win = (0.15 * prior +
           0.2 * home_factor +
           0.3 * elo_factor +
           0.25 * form_factor +
           0.10 * net_factor)

    return win

    


def baysianPredictorAway(team):
    df = pd.read_json("stats.json", orient="columns")
    df = df.T
    df_team = df.loc[team]

    if int(df_team.loc["total_wins"]) == 0:
        return 0.01

    prior = int(df_team.loc["total_wins"]) / int(df_team.loc["games_played"])
    
    away_factor = int(df_team.loc["away_wins"]) / int(df_team.loc["away_games"]) if int(df_team.loc["away_games"]) > 0 else 0.5
    
    elo_factor = norm.cdf((int(df_team.loc["elo"]) - 1500) / 150)
    
    form_factor = int(df_team.loc["last_10_wins"]) / 10
    
    net_factor = norm.cdf(int(df_team.loc["avg_point_diff"]) / 5)

    win = (0.15 * prior +
           0.20 * away_factor +
           0.30 * elo_factor +
           0.25 * form_factor +
           0.10 * net_factor)

    return win





    


def predict(home_team, away_team, is_home_b2b, is_away_b2b):
    p_home = baysianPredictorHome(home_team)
    p_away = baysianPredictorAway(away_team)

    #     # after all other steps
    # if is_home_b2b:
    #     p_home = p_home * 0.95  # 15% penalty for B2B
    
    # if is_away_b2b:
    #     p_away = p_away * 0.95
    

    prob = p_home / (p_home + p_away)
    winner = home_team if prob > 0.5 else away_team


    return winner, prob


