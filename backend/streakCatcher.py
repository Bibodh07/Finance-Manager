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



def save_to_db(df):
    
    with conn:
        with conn.cursor() as cursor:
            for index, row in df.iterrows():
                cursor.execute(
                    """

                UPDATE fixtures 
                SET is_home_b2b = %s,
                    is_away_b2b = %s
                WHERE game_id = %s


                    """, 
                (
                    (row["is_home_B2B"], row["is_away_B2B"], row["gameID"],)
                )
            )
    




def B2B_flagger(team_code, df):


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





    team = NBA_TEAMS[team_code]

    secondary_df = df[(df["homeTeam"]==team) | (df["awayTeam"]==team)]


    secondary_df = secondary_df.sort_values("gameDate")

    secondary_df["prevDate"] = secondary_df["gameDate"].shift(1)


    secondary_df["gameDate"] = pd.to_datetime(secondary_df["gameDate"])

    secondary_df = secondary_df.sort_values("gameDate")

    secondary_df["prevDate"] = secondary_df["gameDate"].shift(1)

    secondary_df['is_home_B2B'] = (
    (secondary_df["homeTeam"] == team)
    &
    ((secondary_df["gameDate"] - secondary_df["prevDate"]).dt.days == 1)
    )

    secondary_df["is_away_B2B"] = (
    (secondary_df["awayTeam"] == team)
    &
    ((secondary_df["gameDate"] - secondary_df["prevDate"]).dt.days == 1)
    )

    home_b2b = secondary_df[secondary_df["is_home_B2B"]]["gameID"]
    away_b2b = secondary_df[secondary_df["is_away_B2B"]]["gameID"]

    df.loc[df["gameID"].isin(home_b2b), "is_home_B2B"] = True
    df.loc[df["gameID"].isin(away_b2b), "is_away_B2B"] = True




   


   

    return df


def test(df):

    test_df = df.copy()

    home = df[["gameID", "gameDate", "homeTeam"]].rename(columns={"homeTeam": "team"})
    away = df[["gameID", "gameDate", "awayTeam"]].rename(columns={"awayTeam": "team"})

    home_b = home.groupby("team")
    away_b = home.groupby("team")


    test_df["prevDate"] = test_df["gameDate"].shift(1)

    test_df["is_b2b"] = (test_df["gameDate"] - test_df["prevDate"]).dt.day = 1

    test_df["is_home_B2B"] = test_df[(home_b("team").isin(test_df["homeTeam"])) & test_df["is_b2b"]]

  











 














def main():


    teams_df = pd.DataFrame()

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
    with conn:
        with conn.cursor() as curs:
            curs.execute(
                '''
                SELECT * FROM fixtures
                '''
            )
            result = curs.fetchall()


    teams_df = pd.DataFrame(result, columns=["gameID", "homeTeam", "awayTeam", "home_score", "away_score", "winner", "gameDate", "is_home_B2B", "is_away_B2B"])


        
    NBA_TEAMS_ABB = NBA_TEAMS.keys()
    for team in NBA_TEAMS_ABB:
        result = B2B_flagger(team_code=team, df=teams_df)
        teams_df = result
    

    print(teams_df.query("homeTeam == 'Golden State Warriors' or awayTeam == 'Golden State Warriors'"))

    # test(df=teams_df)




    teams_df = teams_df.sort_values(["team", "gameDate"])
    save_to_db(teams_df)



main()






