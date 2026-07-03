from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import time
import random
from dotenv import load_dotenv, find_dotenv
import requests
import csv
import json
from scipy.stats import linregress
import numpy as np
from psycopg2 import pool
import pandas as pd
from analyticsData import * 
from baysianPredictor import predict as bayes_predict



# ==============================
# APP SETUP
# ==============================

app = Flask(__name__)
CORS(app)  # allow React frontend

load_dotenv(find_dotenv())
API_KEY = os.getenv("API_KEY")


# ==============================
# ENV VARIABLES
# ==============================

REQUIRED_VARS = [
    "data_base",
    "dbuser",
    "dbpassword",
    "dbhost",
    "dbport"
]

for var in REQUIRED_VARS:
    if not os.getenv(var):
        raise ValueError(
            f"Environment variable '{var}' missing"
        )

app.config["data_base"] = os.getenv("data_base")
app.config["dbuser"] = os.getenv("dbuser")
app.config["dbpassword"] = os.getenv("dbpassword")
app.config["dbhost"] = os.getenv("dbhost")
app.config["dbport"] = int(os.getenv("dbport"))

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=app.config["data_base"],
    user=app.config["dbuser"],
    password=app.config["dbpassword"],
    host=app.config["dbhost"],
    port=app.config["dbport"]
)


# ==============================
# DATABASE CONNECTION
# ==============================

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)


# ==============================
# UTIL FUNCTIONS
# ==============================

def createAuniqueKey():
    t = int(time.time() * 1000)
    rand_int = random.randint(1, 100000)
    return t % rand_int


# ⚠️ temporary hashing (upgrade later)
def hashPassword(pw):
    hash_value = 0
    for c in pw:
        hash_value = (hash_value * 31 + ord(c)) % 100000
    return str(hash_value)


def verify(username, password):

    hashed_pw = hashPassword(password)

    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
                SELECT 1
                FROM userdb
                WHERE username=%s
                AND userpassword=%s
                """,
                (username, hashed_pw)
            )

            result = curs.fetchone()

    return result is not None

def getBarcaMatches():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {
        "league": 140,
        "season": 2024,
        "team": 529
    }

    response = requests.get(url, headers=headers, params=params)

    # optional: debug print
    print(response.json())

    return response.json()


def generate_betting_data():
    filename = "barcelona_fixtures.json"
    initial_money = 100

    with open(filename) as f:
        data = json.load(f)

    matches = data['response']
    money = initial_money
    game_history = []

    for match in matches:
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        home_goals = match['goals']['home']
        away_goals = match['goals']['away']

        # Skip matches Barcelona isn't in
        if home != "Barcelona" and away != "Barcelona":
            continue

        if home == "Barcelona":
            team_goals = home_goals
            opp_goals = away_goals
            won = match['teams']['home']['winner']
            home_game = True
        else:
            team_goals = away_goals
            opp_goals = home_goals
            won = match['teams']['away']['winner']
            home_game = False

        gd = team_goals - opp_goals

        # Betting formula
        if won:
            money_change = 2 + 0.5*gd
        elif gd == 0:
            money_change = 1
        else:
            money_change = -1.5 if home_game else -1

        money += money_change

        game_history.append({
            "opponent": away if home == "Barcelona" else home,
            "home_game": home_game,
            "team_goals": team_goals,
            "opp_goals": opp_goals,
            "win": won,
            "goal_difference": gd,
            "money_change": round(money_change,2),
            "current_money": round(money,2)
        })

    return game_history



def getInvestments():

    u_id = 1

    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
              SELECT *
              FROM investments
              Where user_id =%s

                """,
                (u_id,)
            )

            result = curs.fetchall()
    return result


#add investments

def addInvestmentsDB(investment, teamid, teamname):
    u_id = 3
    date = '2023-03-21'
    ammount = 100

    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(
                """
                INSERT INTO investments 
                (user_id, stock_name, amount, date_invested, current_price, teamid)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, teamid)
                DO UPDATE
                SET current_price = investments.current_price + EXCLUDED.current_price;
                """,
                (
                    u_id,
                    teamname,
                    ammount,
                    date,
                    investment,   # assuming current_price starts same as investment
                    teamid
                )
            )
            conn.commit()


def returnTeams():

    with get_connection() as conn:
        with conn.cursor() as curs:
            curs.execute(

                """
                SELECT * 
                FROM teams
                
                """,

            )

            result = curs.fetchall()
    return result





def logIn(userName, passWord):

    try:
        print(userName, passWord)

        with get_connection() as conn:
            with conn.cursor() as curs:

                curs.execute(

                    """
                    SELECT *
                    FROM userdb  
                    WHERE username = %s AND userpassword = %s
                    """,
                    (userName, passWord)
                

                )
                result = curs.fetchall()
                print(result)

    except Exception as e:
        print("Error:", e)
        result = None
        
    
    return result




def getTrendLineData():
    conn = get_connection()
    try:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT team_name, elo_after, game_id 
                FROM eloratings 
                ORDER BY team_name, game_id ASC
            """)
            rows = curs.fetchall()
    finally:
        conn.close()

    teams = {}
    for row in rows:
        team, elo, game_id = row
        if team not in teams:
            teams[team] = []
        teams[team].append((game_id, elo))

    predictions = {}
    for team, history in teams.items():
        x = np.array([h[0] for h in history])
        y = np.array([h[1] for h in history])
        slope, intercept, _, _, _ = linregress(x, y)
        next_game = x[-1] + 1
        predictions[team] = round(intercept + slope * next_game, 2)

    return predictions










# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():

    return jsonify({"message": "Backend running"})

@app.route("/api/barca-fixtures")
def sendData():
    data = getBarcaMatches()
    return jsonify(data)

# API endpoint
@app.route("/api/barca-betting")
def barca_betting():
    data = generate_betting_data()
    return jsonify(data)


@app.route("/get/user-investments")
def userInvestment():
    data = getInvestments()
    return jsonify(data)


@app.route("/add/userInvestment", methods=["POST"])
def addInvestment():

    data = request.json
    print(data)
    amount = data["amount"]
    teamid = data["teamid"]
    teamname = data["teamname"]

    addInvestmentsDB(investment=amount, teamid=teamid, teamname=teamname)

    return jsonify({
        "message": "Investment updated successfully",
        "teamid": teamid,
        "teamname": teamname,
        "amount": amount
    }), 200



@app.route("/get/investment-team")
def getTeams(): 
    listOfTeams = returnTeams()
    print('hi')
    return jsonify(listOfTeams)

@app.route("/login", methods = ["POST"])
def logInveri():
    data = request.json
    userName = data['username']
    password = data['password']
    result = logIn(userName, password)

    print(result)

    frResult = True if result else False

    

    return jsonify({
        "successStatus":frResult
    }),200





@app.route("/current-market-data")
def currentMarketdata():
    conn = get_connection()
    try:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT DISTINCT ON (team_name) team_name, elo_before
                FROM eloRatings
                ORDER BY team_name, game_id ASC
            """)
            starting = {row[0]: row[1] for row in curs.fetchall()}

            curs.execute("""
                SELECT DISTINCT ON (team_name) team_name, elo_after
                FROM eloRatings
                ORDER BY team_name, game_id DESC
            """)
            current = {row[0]: row[1] for row in curs.fetchall()}

            data = [
                {
                    "team": team,
                    "starting_elo": starting[team],
                    "current_elo": current[team]
                }
                for team in current
            ]
            return jsonify(data)
    finally:
        release_connection(conn)


@app.route("/elo/<team>")
def get_elo_history(team):
    conn = get_connection()
    try:
        with conn.cursor() as curs:
            curs.execute(
                "SELECT predicted_elo, elo_after, game_id FROM eloRatings WHERE team_name = %s ORDER BY game_id ASC",
                (team,)
            )
            rows = curs.fetchall()  
            data = [{"game_id": row[2], "elo": row[1], "predicted": row[0]} for row in rows]
            return jsonify(data)
    finally:
        release_connection(conn)


@app.route("/elo-trend-line")
def eloTrendLine():  
    conn = get_connection()
    try:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT DISTINCT ON (team_name) team_name, elo_after
                FROM eloRatings
                ORDER BY team_name, game_id DESC
            """)
            actual_ratings = {row[0]: row[1] for row in curs.fetchall()}  # inside cursor block now
            predicted_ratings = getTrendLineData() 
            return jsonify({
                "actual": actual_ratings,
                "predicted": predicted_ratings
            })
    finally:
        release_connection(conn)

@app.route("/team-stats")
def team_stats():
    with open("stats.json") as f:
        stats = json.load(f)
    return jsonify(stats)

@app.route("/team-b2b")
def team_b2b():
    conn = get_connection()
    try:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM fixtures")
            fixtures = curs.fetchall()
    finally:
        release_connection(conn)

    df = pd.DataFrame(fixtures, columns=["gameid", "homeTeam", "awayTeam", "homeScore", "awayScore", "winner", "game_date", "isHomeB2B", "isAwayB2B"])
    
    # count B2Bs per team
    home_b2b = df[df["isHomeB2B"] == True].groupby("homeTeam").size().reset_index(name="b2b_count")
    home_b2b.columns = ["team", "b2b_count"]
    
    away_b2b = df[df["isAwayB2B"] == True].groupby("awayTeam").size().reset_index(name="b2b_count")
    away_b2b.columns = ["team", "b2b_count"]

    combined = pd.concat([home_b2b, away_b2b]).groupby("team")["b2b_count"].sum().reset_index()
    
    return jsonify(combined.to_dict(orient="records"))


@app.route("/game-analytics/<home_team>/<away_team>")
def game_analytics(home_team, away_team):
    is_home_b2b = request.args.get("isHomeB2B", "false").lower() == "true"
    is_away_b2b = request.args.get("isAwayB2B", "false").lower() == "true"

    
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

    # expected points
    expected = expectedPointsPerGame(
        homeTeam=home_team,
        awayTeam=away_team,
        isB2B_home=is_home_b2b,
        isB2B_away=is_away_b2b
    )

    # bayesian win probability
    predicted_winner, prob = bayes_predict(
        home_team=home_team,
        away_team=away_team,
        is_home_b2b=is_home_b2b,
        is_away_b2b=is_away_b2b
    )

    # confidence interval on expected points using std from stats.json
    import json
    from scipy.stats import norm
    with open("stats.json") as f:
        stats = json.load(f)

    home_std = stats[home_team]["avg_point_diff"]  # proxy for std for now
    away_std = stats[away_team]["avg_point_diff"]

    home_pts = expected["home"]["expected_points"]
    away_pts = expected["away"]["expected_points"]

    return jsonify({
        "expected_points": expected,
        "prediction": {
            "winner": predicted_winner,
            "probability": round(prob, 2)
        },
        "confidence_intervals": {
            "home": {
                "lower": round(home_pts - 1.96 * abs(home_std), 1),
                "upper": round(home_pts + 1.96 * abs(home_std), 1)
            },
            "away": {
                "lower": round(away_pts - 1.96 * abs(away_std), 1),
                "upper": round(away_pts + 1.96 * abs(away_std), 1)
            }
        },
        "home_player": playerToWatch(NAME_TO_ABB.get(home_team, home_team)),
        "away_player": playerToWatch(NAME_TO_ABB.get(away_team, away_team))
    })

    







if __name__ == "__main__":
    app.run(debug=True)
