import json
import pandas as pd




def expectedPointsPerGame(homeTeam, awayTeam, isB2B_home, isB2B_away):

    df = pd.read_json("points_test.json", orient="columns")
    df = df.T

    home_team = df.loc[homeTeam]
    away_team = df.loc[awayTeam]

    # Step 1: baseline expected points (overall average)
    home_expected = home_team["avg_points"]
    away_expected = away_team["avg_points"]

    print(f"Step 1 - Baseline: home={home_expected}, away={away_expected}")

    # Step 2: home/away adjustment
    home_expected = home_team["home_avg_points"]
    away_expected = away_team["away_avg_points"]

    print(f"Step 2 - Home/Away adjusted: home={home_expected}, away={away_expected}")

    # Step 3: B2B penalty
    if isB2B_home:
        home_expected -= 3
    if isB2B_away:
        away_expected -= 3

    print(f"Step 3 - B2B adjusted: home={home_expected}, away={away_expected}")

    return home_expected, away_expected


print(expectedPointsPerGame(homeTeam="GSW", awayTeam="LAL", isB2B_away=False, isB2B_home=False))

