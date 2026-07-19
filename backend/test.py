import pandas as pd 
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os
import pandas

load_dotenv(find_dotenv())


def getPlayerAnalytics():

    with psycopg2.connect(
        dbname=os.getenv("data_base"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpassword"),
        host=os.getenv("dbhost"),
        port=int(os.getenv("dbport"))
    ) as conn:
        player_df = pd.read_sql(
            "SELECT * FROM playerDB ORDER BY overall_score DESC LIMIT 5",
            conn,

        )

    print(player_df)
    return player_df


def getPlayerAnalyticsOfAparticularPlayer(name):

    with psycopg2.connect(
        dbname=os.getenv("data_base"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpassword"),
        host=os.getenv("dbhost"),
        port=int(os.getenv("dbport"))
    ) as conn:
        player_df = pd.read_sql(
            "SELECT * FROM playerDB WHERE name = %s",
            conn,
            params=(name,)
        )

    print(player_df)
    return player_df

def getScatterPlotData():
        team_df = pd.read_json("stats.json").T


        team_df = team_df.loc[:, ["avg_point_scored", "avg_point_allowed"]]

        print(team_df)

getScatterPlotData()
