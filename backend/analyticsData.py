import json
import pandas as pd




def expectedPointsPerGame(homeTeam, awayTeam, isB2B_home, isB2B_away):

    df = pd.read_json("stats.json", orient="columns")
    df = df.T

    home_team = df.loc[homeTeam]
    away_team = df.loc[awayTeam]

    # Step 1: baseline expected points (overall average)
    home_expected = home_team["avg_point_scored"]
    away_expected = away_team["avg_point_scored"]

    print(f"Step 1 - Baseline: home={home_expected}, away={away_expected}")

    # Step 2: home/away adjustment
    home_expected = home_team["avgHomePointScored"]
    away_expected = away_team["avgAwayPointScored"]

    print(f"Step 2 - Home/Away adjusted: home={home_expected}, away={away_expected}")

    # Step 3: B2B penalty
    if isB2B_home:
        home_expected -= 3
    if isB2B_away:
        away_expected -= 3

    print(f"Step 3 - B2B adjusted: home={home_expected}, away={away_expected}")

    return home_expected, away_expected


print(expectedPointsPerGame(homeTeam="Golden State Warriors", awayTeam="Oklahoma City Thunder", isB2B_away=False, isB2B_home=False))

