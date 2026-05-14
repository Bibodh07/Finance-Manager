from bs4 import BeautifulSoup
import httpx
import json
from pathlib import Path
import pandas as pd


def getFixtures():
    url = "https://www.basketball-reference.com/leagues/NBA_2026_games-october.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }

    req = httpx.get(url, headers=headers)
    soup = BeautifulSoup(req.text, 'lxml')
    fixtures = soup.find("table", id="schedule")

    for line in fixtures:
        if line.name and line.name == "tbody":
            visitor_pts = line.find_all("td", attrs={"data-stat": "visitor_pts"})
            home_pts = line.find_all("td", attrs={"data-stat": "home_pts"})
            visitorTeamname = line.find_all("td", attrs={"data-stat": "visitor_team_name"})
            homeTeamname = line.find_all("td", attrs={"data-stat": "home_team_name"})

    games = []
    for i in range(len(visitor_pts)):
        game = {
            "visitor": {
                "team": visitorTeamname[i].text,
                "score": visitor_pts[i].text
            },
            "home": {
                "team": homeTeamname[i].text,
                "score": home_pts[i].text
            }
        }
        games.append(game)

    with open("fixtures.json", "w") as f:
        json.dump(games, f, indent=4)

    print(f"Saved {len(games)} games to fixtures.json")


def simulate():
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

    visitorScore = homeScore = 0
    visitorTeam = homeTeam = None

    df_fixtures = pd.read_json("fixtures.json")
    for i in range(len(df_fixtures)):
        fixtures = df_fixtures.loc[i]
        for team, score in fixtures.items():

            teamName, gameScore = score.values()

            if team == "visitor":
                visitorScore = gameScore
                visitorTeam = teamName
            else:
                homeScore = gameScore
                homeTeam = teamName

            if homeTeam and visitorTeam:
                if int(homeScore) > int(visitorScore):
                    winner = homeTeam
                else:
                    winner = visitorTeam

                print(f"{winner} won")
                updateEloRatings(NAME_TO_ABB[visitorTeam], NAME_TO_ABB[homeTeam], NAME_TO_ABB[winner])
                homeTeam = visitorTeam = None
            else:
                continue


def updateEloRatings(team1, team2, winner, K=20):

    with open("elo.json") as f:
        elo_dict = json.load(f)

    R1 = elo_dict[team1]
    R2 = elo_dict[team2]

    P1 = 1 / (1 + 10 ** ((R2 - R1) / 400))
    P2 = 1 - P1

    actual1 = 1 if winner == team1 else 0
    actual2 = 1 - actual1

    elo_dict[team1] = R1 + K * (actual1 - P1)
    elo_dict[team2] = R2 + K * (actual2 - P2)

    with open("elo.json", "w") as f:
        json.dump(elo_dict, f, indent=4)
    
        
    
        
    


       

def main():

    if Path("fixtures.json").exists():
        simulate()
    else:
        getFixtures()

main()



