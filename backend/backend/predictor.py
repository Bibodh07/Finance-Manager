from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
import json
import pandas as pd
import numpy
from scipy.stats import zscore, norm






def getDataInJson():

    load_dotenv(find_dotenv())


    conn = psycopg2.connect(
        dbname=os.getenv("data_base"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpassword"),
        host=os.getenv("dbhost"),
        port=int(os.getenv("dbport"))
    )

    cursor = conn.cursor()



    cursor.execute("SELECT * FROM fixtures")
    rows = cursor.fetchall()
    

    columns = [desc[0] for desc in cursor.description]
    
    all_games = [dict(zip(columns, row)) for row in rows]
    

    for game in all_games:
        if "game_date" in game:
            game["game_date"] = str(game["game_date"])
    
    with open("fixtures.json", "w") as f:
        json.dump(all_games, f, indent=4)
    
    print(f"Exported {len(all_games)} games to fixtures.json")


def build_power_score(team):
    elo_data_df = pd.read_json("elo_data.json")

    with open("elo.json") as f:
        elo_dict = json.load(f)

    elo_df = pd.DataFrame(list(elo_dict.items()), columns=["team", "elo"])
    
    # merge into one df
    df = elo_data_df.merge(elo_df, on="team")

    # normalize across ALL 30 teams first
    df["elo_z"]       = zscore(df["elo"])
    df["srs_z"]       = zscore(df["srs"])
    df["win_pyth_z"]  = zscore(df["win_pyth"])
    df["lose_pyth_z"] = zscore(df["lose_pyth"])
    df["ortg_z"]      = zscore(df["ortg"])
    df["drtg_z"]      = zscore(df["drtg"])

    # then look up the specific team
    row = df[df["team"] == team].iloc[0]

    score = (
    norm.cdf(row["elo_z"])      * 0.30 +
    norm.cdf(row["srs_z"])      * 0.25 +
    norm.cdf(row["win_pyth_z"]) * 0.20 +
    (1 - norm.cdf(row["lose_pyth_z"])) * 0.10 +
    norm.cdf(row["ortg_z"])     * 0.10 +
    (1 - norm.cdf(row["drtg_z"])) * 0.05
      )



    return score



def predict(team1, team2):
    s1 = build_power_score(team1)
    s2 = build_power_score(team2)
    
    prob = s1 / (s1 + s2)
    winner = team1 if prob > 0.5 else team2
    
    print(f"{team1} vs {team2} → {winner} wins with {prob:.0%} confidence")
  
    return winner, prob



def test():

    NBA_TEAMS = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "CHO": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "Los Angeles Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards"
    }

    NAME_TO_ABB = {v: k for k, v in NBA_TEAMS.items()}





    with open("fixtures.json") as f:
        fixtures = json.load(f)

    correct = 0
    total = 0
   

    for game in fixtures:
        home = NAME_TO_ABB.get(game["home_team"])
        visitor = NAME_TO_ABB.get(game["visitor_team"])
        actual_winner = NAME_TO_ABB.get(game["winner"])

        
        try:
            
            predicted_winner, prob = predict(home, visitor)
            
            if predicted_winner == actual_winner:
                correct += 1
            total += 1
        except:
            continue

    print(f"Accuracy: {correct/total:.0%} ({correct}/{total} games)")


    
    
test()