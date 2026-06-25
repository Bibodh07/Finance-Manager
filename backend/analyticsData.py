import json
import pandas as pd


def expectedPointsPerGame(homeTeam, awayTeam, isB2B_home, isB2B_away):

    df = pd.read_json("stats.json", orient="columns")
    df = df.T

    home_team = df.loc[homeTeam]
    away_team = df.loc[awayTeam]

    # league averages - baseline to measure deviation against
    league_avg_scored = df["avg_point_scored"].mean()
    league_avg_allowed = df["avg_point_allowed"].mean()

    print(f"League avg scored: {league_avg_scored}, League avg allowed: {league_avg_allowed}")

    # Step 1: home/away scoring baseline
    home_expected = home_team["avgHomePointScored"]
    away_expected = away_team["avgAwayPointScored"]

    print(f"Step 1 - Home/Away baseline: home={home_expected}, away={away_expected}")

    # Step 2: opponent defense impact - how far is their defense from league average?
    away_defense_diff = away_team["avgAwayPointAllowed"] - league_avg_allowed
    home_defense_diff = home_team["avgHomePointAllowed"] - league_avg_allowed

    home_expected = home_expected + away_defense_diff
    away_expected = away_expected + home_defense_diff

    print(f"Step 2 - Defense adjusted: home={home_expected}, away={away_expected}")

    # Step 3: B2B penalty - measure actual historical impact
    if isB2B_home:
        home_expected -= 3
    if isB2B_away:
        away_expected -= 3

    print(f"Step 3 - B2B adjusted: home={home_expected}, away={away_expected}")

    return home_expected, away_expected


print(expectedPointsPerGame(homeTeam="Golden State Warriors", awayTeam="Oklahoma City Thunder", isB2B_away=False, isB2B_home=False))