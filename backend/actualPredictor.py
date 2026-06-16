from psycopg2 import pool
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv

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

    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT * FROM 
            fixtures
            """
        )
        fixtures = curs.fetchall()
    
  

        df = pd.DataFrame(fixtures, columns=["gameid", "homeTeam", "awayTeam", "homeScore", "awayScore", "winner", "game_date", "isHomeB2B", "isAwayB2B"])
        df = df.sort_values("game_date").reset_index(drop=True)

        home = df[["game_date", "homeTeam"]].rename(columns={"homeTeam":"Team"})
        away = df[["game_date", "awayTeam"]].rename(columns={"awayTeam":"Team"})
        all_games = pd.concat([home, away]).sort_values("game_date")
        for date, game in df.iterrows():

            current_games = game["game_date"]
            games_tillNow = all_games[all_games["game_date"] < current_games]
            avg_games = games_tillNow.groupby("Team")["game_date"].count().mean()
            print(avg_games)

simulate()






