import os
from dotenv import load_dotenv, find_dotenv
import psycopg2
import numpy as np



load_dotenv(find_dotenv())



conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)






def getPlayerData(teamCode):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT * 
            FROM playerDB 
            WHERE team = %s
            """,
            (teamCode,)
        )
        return cursor.fetchall() 



 
def getMinMax(stat):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT MIN({stat}/games), MAX({stat}/games) FROM playerDB")
        return cursor.fetchone()

def getProduction_Impact_Rating():

    pts_min, pts_max = getMinMax("pts")
    ast_min, ast_max = getMinMax("ast")
    reb_min, reb_max = getMinMax("reb")
    stl_min, stl_max = getMinMax("stl")
    blk_min, blk_max = getMinMax("blk")

    player_catalog = getPlayerData("GSW")

    for player in player_catalog:
        pts_norm = ((player[4]/player[3])) / (pts_max - pts_min)
        ast_norm = (player[5] - ast_min) / (ast_max - ast_min)
        reb_norm = (player[6] - reb_min) / (reb_max - reb_min)
        stl_norm = (player[8] - stl_min) / (stl_max - stl_min)
        blk_norm = (player[9] - blk_min) / (blk_max - blk_min)

        production = (
            pts_norm * 0.4 +
            ast_norm * 0.25 +
            reb_norm * 0.2 +
            stl_norm * 0.1 +
            blk_norm * 0.05
        )
        print(player[1], production)



getProduction_Impact_Rating()
