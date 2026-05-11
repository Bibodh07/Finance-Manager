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


# ==============================
# DATABASE CONNECTION
# ==============================

def get_connection():
    return psycopg2.connect(
        dbname=app.config["data_base"],
        user=app.config["dbuser"],
        password=app.config["dbpassword"],
        host=app.config["dbhost"],
        port=app.config["dbport"]
    )


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






if __name__ == "__main__":
    app.run(debug=True)
