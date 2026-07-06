import pandas as pd 
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())




def get_teamOdds():

    with psycopg2.connect(
        dbname=os.getenv("data_base"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpassword"),
        host=os.getenv("dbhost"),
        port=int(os.getenv("dbport"))
    ) as conn:
        player_df = pd.read_sql(
            "SELECT * FROM eloratings",
            conn,

        )
    player_df["net_rating"] = (player_df["elo_after"]) - (player_df["elo_before"])
    print(player_df)        



get_teamOdds()
