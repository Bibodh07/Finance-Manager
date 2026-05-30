import os
from dotenv import load_dotenv, find_dotenv
import psycopg2

load_dotenv(find_dotenv())

conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)

def safe(val, default=0.0):
    return float(val) if val is not None else default

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
        data = cursor.fetchone()
        print({f"Min_{stat}": data[0], f"Max_{stat}": data[1]})
    return {f"Min_{stat}": data[0], f"Max_{stat}": data[1]}

def getDataOnce():
    main_data = []
    relevant_stats = [
        "pts", "ast", "reb", "tov", "stl", "blk", "ws",
        "vorp", "pmon", "pmnet", "ts_pts", "efg", "ts_percent"
    ]
    for stat in relevant_stats:
        main_data.append(getMinMax(stat))
    return main_data

def save_ratings(name, production, impact, overAll_score):
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE playerDB
                SET production_score = %s,
                    impact_score = %s,
                    overall_score = %s

                WHERE name = %s
                """,
                (production, impact, overAll_score, name,)
            )

def resetAndReload():
    print("Resetting production and impact scores...")
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE playerDB
                SET production_score = NULL,
                    impact_score = NULL
                """
            )
    print("Reset complete, recalculating...")

def getProduction_Impact_Rating(player_catalog, mainData):
    pts_min,   pts_max   = mainData[0]["Min_pts"],   mainData[0]["Max_pts"]
    ast_min,   ast_max   = mainData[1]["Min_ast"],   mainData[1]["Max_ast"]
    reb_min,   reb_max   = mainData[2]["Min_reb"],   mainData[2]["Max_reb"]
    tov_min,   tov_max   = mainData[3]["Min_tov"],   mainData[3]["Max_tov"]
    stl_min,   stl_max   = mainData[4]["Min_stl"],   mainData[4]["Max_stl"]
    blk_min,   blk_max   = mainData[5]["Min_blk"],   mainData[5]["Max_blk"]
    ws_min,    ws_max    = mainData[6]["Min_ws"],    mainData[6]["Max_ws"]
    vorp_min,  vorp_max  = mainData[7]["Min_vorp"],  mainData[7]["Max_vorp"]
    pmon_min,  pmon_max  = mainData[8]["Min_pmon"],  mainData[8]["Max_pmon"]
    pmnet_min, pmnet_max = mainData[9]["Min_pmnet"], mainData[9]["Max_pmnet"]





    for player in player_catalog:
            

        
            games = safe(player[3], default=1.0)  

            pts_norm   = ((safe(player[4])/games)  - pts_min)   / (pts_max   - pts_min)
            ast_norm   = ((safe(player[5])/games)  - ast_min)   / (ast_max   - ast_min)
            reb_norm   = ((safe(player[6])/games)  - reb_min)   / (reb_max   - reb_min)
            tov_norm   = ((safe(player[7])/games)  - tov_min)   / (tov_max   - tov_min)
            stl_norm   = ((safe(player[8])/games)  - stl_min)   / (stl_max   - stl_min)
            blk_norm   = ((safe(player[9])/games)  - blk_min)   / (blk_max   - blk_min)
            ws_norm    = ((safe(player[12])/games) - ws_min)    / (ws_max    - ws_min)
            vorp_norm  = ((safe(player[13])/games) - vorp_min)  / (vorp_max  - vorp_min)
            pmon_norm  = ((safe(player[14])/games) - pmon_min)    / (pmon_max  - pmon_min)
            pmnet_norm = ((safe(player[15]) / games) - pmnet_min) / (pmnet_max - pmnet_min)




            production = (
            pts_norm  * 0.4  +
            ast_norm  * 0.25 +
            reb_norm  * 0.2  +
            stl_norm  * 0.1  +
            blk_norm  * 0.05 -
            tov_norm  * 0.1
            )

            impact = (
            ws_norm    * 0.4  +
            vorp_norm  * 0.35 +
            pmon_norm  * 0.15 +
            pmnet_norm * 0.10
            )

            availability = safe(player[3]) / 82  

            player_score = (
            production   * 0.35 +
            impact       * 0.45 +
            availability * 0.20
            )

       

            save_ratings(player[1], production=production, impact=impact, overAll_score=player_score)
            print(f"player:{player[1]} Prod: {production}, impact: {impact}, playerScore= {player_score}")

def main():
    resetAndReload()

    main_data = getDataOnce()

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

    for team in NBA_TEAMS.keys():
        players = getPlayerData(team)
        getProduction_Impact_Rating(players, main_data)

    conn.commit()
    conn.close()
    print("Done.")

main()