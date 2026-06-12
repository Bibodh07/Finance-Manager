import pandas as pd 
import json 
from scipy.stats import zscore, norm







def baysianPredictorHome(team):


    df = pd.read_json("testData.json", orient="columns")
    df = df.T

    df_team = df.loc[team]


    # Step 1 
    # Get P wins 

    win = int(df_team.loc["total_wins"])/ int(df_team.loc["games_played"])
    print(f'Step 1: wins: {win}')

    #Step 2 
    # Use Step 1 to get prob. of wins given they play at home 

    home_wins = int(df_team.loc["home_wins"])/int(df_team.loc["total_wins"])
    home_games = int(df_team.loc["home_games"])/int(df_team.loc["games_played"])

    win = home_wins/home_games * win #likelyhood ratio * total wins

    print(f'Step 2: P(win|home): {win}')


    #step 3 
    # Use step 2 to find the win probability given team strenght of each teams 

    elo = int(df_team.loc["elo"])
    z_score = (elo - 1500)/150

    elo_percentile = norm.cdf(z_score)

    win = (elo_percentile / 0.5) * win
    print(f'Step 3: P(win|elo): {win}')

    #Step 4
    # use form 

    form = int(df_team.loc["last_10_wins"])/10

    win  = (form/0.5) * win
    print(f'Step 4: P(win|form): {win}')

    # Step 5 
    # use net rating 

    net_diff = int(df_team.loc["avg_point_diff"])
    z_score = (net_diff - 0)/ 5
    net_rating = norm.cdf(z_score)

    win = (net_rating/0.5) * win 
    print(f'Step 4: P(win|net rating): {win}')

    return win

    






    

def baysianPredictorAway(team):

    df = pd.read_json("testData.json", orient="columns")
    df = df.T

    df_team = df.loc[team]

    # Step 1
    win = int(df_team.loc["total_wins"]) / int(df_team.loc["games_played"])
    print(f'Step 1: wins: {win}')

    # Step 2 - away factor
    away_wins = int(df_team.loc["away_wins"]) / int(df_team.loc["total_wins"])
    away_games = int(df_team.loc["away_games"]) / int(df_team.loc["games_played"])
    win = away_wins / away_games * win
    print(f'Step 2: P(win|away): {win}')

    # Step 3 - elo
    elo = int(df_team.loc["elo"])
    z_score = (elo - 1500) / 150
    elo_percentile = norm.cdf(z_score)
    win = (elo_percentile / 0.5) * win
    print(f'Step 3: P(win|elo): {win}')

    # Step 4 - form
    form = int(df_team.loc["last_10_wins"]) / 10
    win = (form / 0.5) * win
    print(f'Step 4: P(win|form): {win}')

    # Step 5 - net rating
    net_diff = int(df_team.loc["avg_point_diff"])
    z_score = (net_diff - 0) / 5
    net_rating = norm.cdf(z_score)
    win = (net_rating / 0.5) * win
    print(f'Step 5: P(win|net rating): {win}')

    return win


def predict(home_team, away_team):
    p_home = baysianPredictorHome(home_team)
    p_away = baysianPredictorAway(away_team)

    prob = p_home / (p_home + p_away)
    winner = home_team if prob > 0.5 else away_team

    print(f'\n{home_team} vs {away_team} → {winner} wins with {prob:.0%} confidence')
    return winner, prob



predict(home_team = "GSW", away_team= "LAL")