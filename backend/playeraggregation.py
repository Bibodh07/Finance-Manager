import psycopg2
import os
import json 
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)

def get_aggregate_rating(teamCode):
    
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(

                """
               SELECT AVG(overall_score)
               FROM (
                 SELECT overall_score 
                 FROM playerDB
                 WHERE team = %s
                 ORDER BY overall_score DESC
                 LIMIT 8
                 
               )top8


                """,
                (teamCode,)

            )

            result = cursor.fetchall()
    return(float(result[0][0]))



print(f'the rarings for OKC {get_aggregate_rating('OKC') * 100} vs WAS {get_aggregate_rating('WAS') * 100}')




