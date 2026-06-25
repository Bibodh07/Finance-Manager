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

    total = correct = 0


    stats = {}





    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT * FROM 
            fixtures
            """
        )
        fixtures = curs.fetchall()


        player_df = pd.read_sql("SELECT * FROM playerdb", conn)
        team_overall = player_df.groupby("team")["overall_score"].mean().to_dict()


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



    for _, game in df.iterrows():

        current_games = game["game_date"]
        games_tillNow = all_games[all_games["game_date"] < current_games]
        avg_games = games_tillNow.groupby("Team")["game_date"].count().mean()


        if pd.isna(avg_games) or avg_games < 10:
                predicted_winner, prob = power_predict(team1=NAME_TO_ABB[game["homeTeam"]], team2=NAME_TO_ABB[game["awayTeam"]])

        else:
                predicted_winner, prob = bayes_predict(home_team=game["homeTeam"], away_team=game["awayTeam"], is_home_b2b=game["isHomeB2B"], is_away_b2b=game["isAwayB2B"])

        

        actual_winner = game["winner"]




        if predicted_winner == actual_winner:
            correct += 1
        total += 1


        print(f'\n{game["homeTeam"]} vs {game["awayTeam"]} → Predicted Winner {predicted_winner} wins with {prob:.0%} confidence \n Actual Winner = {actual_winner}')


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
                "elo": 1500 + (team_overall.get(NAME_TO_ABB[team], 0.5) - 0.5) * 200,
                "last_10_diffs": [],
                "last_10_results":[],
                "points_allowedHistory":[],
                "home_pointsAllowedHistory": [],
                "away_pointsAllowedHistory": [],
                "avg_point_allowed": 0,
                "avgHomePointAllowed": 0,
                "avgAwayPointAllowed": 0,
                "avg_point_scored": 0,
                "points_scoredHistory":[],
                "avgHomePointScored": 0,
                "avgAwayPointScored": 0,
                "home_pointsScoredHistory": [],
                "away_pointsScoredHistory": [],
                "b2b_scoringHistory": [],
                "b2b_defenseHistory": [],
                "average_score_onb2b": 0,
                "average_defensive_recrod_onb2b": 0,

            }
            
           
    # always update regardless
            stats[team]["games_played"] += 1
    
            if game["winner"] == team:
                stats[team]["total_wins"] += 1
    
            if game["homeTeam"] == team:
                stats[team]["home_games"] += 1
                stats[team]["home_pointsAllowedHistory"].append(game["awayScore"])
                stats[team]["home_pointsScoredHistory"].append(game["homeScore"])
                if game["winner"] == team:
                    stats[team]["home_wins"] += 1
            else:
                stats[team]["away_games"] += 1
                stats[team]["away_pointsAllowedHistory"].append(game["homeScore"])
                stats[team]["away_pointsScoredHistory"].append(game["awayScore"])
                if game["winner"] == team:
                    stats[team]["away_wins"] += 1
    

            stats[team]["last_10_results"].append(1 if game["winner"] == team else 0)
            stats[team]["last_10_results"] = stats[team]["last_10_results"][-10:]  
            stats[team]["last_10_wins"] = sum(stats[team]["last_10_results"])
            stats[team]["points_allowedHistory"].append(game["homeScore"] if team == game["awayTeam"] else game["awayScore"])
            stats[team]["avg_point_allowed"] = sum(stats[team]["points_allowedHistory"])/len(stats[team]["points_allowedHistory"])
            stats[team]["points_scoredHistory"].append(game["homeScore"] if team == game["homeTeam"] else game["awayScore"])
            stats[team]["avg_point_scored"] = sum(stats[team]["points_scoredHistory"])/len(stats[team]["points_scoredHistory"])


            if len(stats[team]["home_pointsAllowedHistory"]) > 0:
                stats[team]["avgHomePointAllowed"] = sum(stats[team]["home_pointsAllowedHistory"]) / len(stats[team]["home_pointsAllowedHistory"])

            if len(stats[team]["away_pointsAllowedHistory"]) > 0:
                stats[team]["avgAwayPointAllowed"] = sum(stats[team]["away_pointsAllowedHistory"]) / len(stats[team]["away_pointsAllowedHistory"])

            if len(stats[team]["home_pointsScoredHistory"]) > 0:
                stats[team]["avgHomePointScored"] = sum(stats[team]["home_pointsScoredHistory"]) / len(stats[team]["home_pointsScoredHistory"])

            if len(stats[team]["away_pointsScoredHistory"]) > 0:
                stats[team]["avgAwayPointScored"] = sum(stats[team]["away_pointsScoredHistory"]) / len(stats[team]["away_pointsScoredHistory"])
   
            if game["homeTeam"] == team:
                point_diff = int(game["homeScore"]) - int(game["awayScore"])
            else:
                point_diff = int(game["awayScore"]) - int(game["homeScore"])

            stats[team]["last_10_diffs"].append(point_diff)
            stats[team]["last_10_diffs"] = stats[team]["last_10_diffs"][-10:]
            stats[team]["avg_point_diff"] = sum(stats[team]["last_10_diffs"]) / len(stats[team]["last_10_diffs"])

        winner = game["winner"]
        loser = game["awayTeam"] if game["winner"] == game["homeTeam"] else game["homeTeam"]

        winner_elo = stats[winner]["elo"]
        loser_elo = stats[loser]["elo"]

        expected_winner = 1 / (1 + 10**((loser_elo - winner_elo) / 400))
        expected_loser = 1 - expected_winner

        stats[winner]["elo"] = winner_elo + 20 * (1 - expected_winner)
        stats[loser]["elo"] = loser_elo + 20 * (0 - expected_loser)



        with open("stats.json", "w") as f:
            json.dump(stats, f, indent=4)



    print(f"Accuracy: {correct/total:.0%} ({correct}/{total} games)")

        

    

            


           
            
    
  



        
             



simulate()






