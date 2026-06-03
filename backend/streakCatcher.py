'''

GOAL: 
Create a Streak calculator (1) 
Create a B2B flagger

'''


from datetime import * 
import psycopg2
from dotenv import load_dotenv, find_dotenv
import pandas as pd
import os



load_dotenv(find_dotenv())


conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)





# d1 = datetime.today().date()
# d2 = datetime.strptime('01/06/26',
#                      '%d/%m/%y').date()

# print(type(d2))



# print(d2-d1)  referecne



def B2B_flagger():
    with conn:
        with conn.cursor() as curs:
            curs.execute(
                '''
                SELECT * FROM fixtures
                '''
            )
            result = curs.fetchall()
    print(result)



B2B_flagger()