import json
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def expectedPointsPerGame(homeTeam, awayTeam, isB2B_home, isB2B_away):

    df = pd.read_json("stats.json", orient="columns")
    df = df.T

    home_team = df.loc[homeTeam]
    away_team = df.loc[awayTeam]

    # league averages
    league_avg_scored = df["avg_point_scored"].mean()
    league_avg_allowed = df["avg_point_allowed"].mean()

    # Step 1: home/away scoring baseline
    home_expected = home_team["avgHomePointScored"]
    away_expected = away_team["avgAwayPointScored"]

    # Step 2: opponent defense impact
    away_defense_diff = away_team["avgAwayPointAllowed"] - league_avg_allowed
    home_defense_diff = home_team["avgHomePointAllowed"] - league_avg_allowed

    home_expected = home_expected + away_defense_diff
    away_expected = away_expected + home_defense_diff

    # Step 3: B2B penalty
    if isB2B_home:
        if home_team["average_score_onb2b"] != 0:
            b2b_impact = home_team["average_score_onb2b"] - home_team["avg_point_scored"]
            home_expected += b2b_impact

    if isB2B_away:
        if away_team["average_score_onb2b"] != 0:
            b2b_impact = away_team["average_score_onb2b"] - away_team["avg_point_scored"]
            away_expected += b2b_impact

    # expected defense = opponent's expected score
    home_expected_allowed = away_expected
    away_expected_allowed = home_expected

    return {
        "home": {
            "expected_points": round(home_expected, 1),
            "expected_points_allowed": round(home_expected_allowed, 1)
        },
        "away": {
            "expected_points": round(away_expected, 1),
            "expected_points_allowed": round(away_expected_allowed, 1)
        }
    }

def playerToWatch(team_abbr):
    with psycopg2.connect(
        dbname=os.getenv("data_base"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpassword"),
        host=os.getenv("dbhost"),
        port=int(os.getenv("dbport"))
    ) as conn:
        player_df = pd.read_sql(
            "SELECT name, overall_score, pts, ast, reb FROM playerdb WHERE team = %s ORDER BY overall_score DESC LIMIT 1",
            conn,
            params=(team_abbr,)
        )
    return player_df.iloc[0].to_dict()





print (
    f"For Golden State Warriors game:\n Expected points for GSW and LAL are {expectedPointsPerGame(homeTeam="Golden State Warriors", awayTeam="Los Angeles Lakers", isB2B_away=True, isB2B_home=False)}\n Players to watch {playerToWatch('GSW')} and {playerToWatch("LAL")}"
)