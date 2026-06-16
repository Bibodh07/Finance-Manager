from psycopg2 import pool
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
from predictor import predict as power_predict
from baysianPredictor import predict as bayes_predict
import json


"""
Goal is to make a predictor based on bayes theorm;
Taking a win probability and then adding factors such as 
form, player age, player rating, power, fixture etc to create an accurate prediction


mathcmatical probability for form
"""

load_dotenv(find_dotenv())


conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)



def simulate():


    stats = {}

    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT * FROM 
            fixtures
            """
        )
        fixtures = curs.fetchall()


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
    
  

    df = pd.DataFrame(fixtures, columns=["gameid", "homeTeam", "awayTeam", "homeScore", "awayScore", "winner", "game_date", "isHomeB2B", "isAwayB2B"])
    df = df.sort_values("game_date").reset_index(drop=True)

    home = df[["game_date", "homeTeam"]].rename(columns={"homeTeam":"Team"})
    away = df[["game_date", "awayTeam"]].rename(columns={"awayTeam":"Team"})
    all_games = pd.concat([home, away]).sort_values("game_date")



    for date, game in df.iterrows():

        current_games = game["game_date"]
        games_tillNow = all_games[all_games["game_date"] < current_games]
        avg_games = games_tillNow.groupby("Team")["game_date"].count().mean()

        if avg_games < 10:
                power_predict(team1=NAME_TO_ABB[game["homeTeam"]], team2=NAME_TO_ABB[game["awayTeam"]])

        else:
                bayes_predict(home_team=game["homeTeam"], away_team=game["awayTeam"])


        #data update begins here.

        for team in [game["homeTeam"], game["awayTeam"]]:
            if team not in stats:
                stats[team] = {
                "games_played": 0,
                "total_wins": 0,
                "home_games": 0,
                "home_wins": 0,
                "away_games": 0,
                "away_wins": 0,
                "last_10_wins": 0,
                "avg_point_diff": 0,
                "elo": 1500,
                "last_10_diffs": [],
                "last_10_results":[]
            }
            
           
    # always update regardless
            stats[team]["games_played"] += 1
    
            if game["winner"] == team:
                stats[team]["total_wins"] += 1
    
            if game["homeTeam"] == team:
                stats[team]["home_games"] += 1
                if game["winner"] == team:
                    stats[team]["home_wins"] += 1
            else:
                stats[team]["away_games"] += 1
                if game["winner"] == team:
                    stats[team]["away_wins"] += 1
    

            stats[team]["last_10_results"].append(1 if game["winner"] == team else 0)
            stats[team]["last_10_results"] = stats[team]["last_10_results"][-10:]  # keep only last 10
            stats[team]["last_10_wins"] = sum(stats[team]["last_10_results"])
            
    
            
        # point diff for this game
            if game["homeTeam"] == team:
                point_diff = int(game["homeScore"]) - int(game["awayScore"])
            else:
                point_diff = int(game["awayScore"]) - int(game["homeScore"])

            stats[team]["last_10_diffs"].append(point_diff)
            stats[team]["last_10_diffs"] = stats[team]["last_10_diffs"][-10:]
            stats[team]["avg_point_diff"] = sum(stats[team]["last_10_diffs"]) / len(stats[team]["last_10_diffs"])

        with open("stats.json", "w") as f:
            json.dump(stats, f, indent=4)
    

            


           
            
    
  



        
             



simulate()






