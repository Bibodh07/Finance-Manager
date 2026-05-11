from bs4 import BeautifulSoup
import httpx
import json
import regex as re
import pandas as pd

def convert_streak(x):
    parts = x.split()
    print(parts[1])
    sign = 1 if parts[0] == "W" else -1
    return sign * int(parts[1])


def get_team_games(team_code):

    url = f"https://www.basketball-reference.com/teams/{team_code}/2026_games.html"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }

    req = httpx.get(url, headers=headers)

    if req.status_code != 200:
        print(f"Request failed: {req.status_code}")
        return []

    html = BeautifulSoup(req.text, "lxml")

    fixtures = html.find("tbody")

    if not fixtures:
        print("No table found")
        return []

    relevant_data = {
        "opp_name",
        "game_result",
        "pts",
        "opp_pts",
        "wins",
        "losses",
        "game_streak"
    }

    games = fixtures.find_all("tr")

    all_games = []

    for game in games:

        game_data = {}

        for attr in game.find_all(["td", "th"]):

            stat = attr.get("data-stat")

            if stat in relevant_data:

                value = attr.get_text(strip=True)

                # convert streak into numeric
                if stat == "game_streak":
                    if attr.get_text() != 'Streak':
                        value = convert_streak(value)

                # convert numeric fields
                if stat in ["pts", "opp_pts", "wins", "losses"]:
                    try:
                        value = int(value)
                    except:
                        pass

                game_data[stat] = value

        if game_data:
            all_games.append(game_data)

    return all_games




def getStartingElo():
    url = "https://www.basketball-reference.com/teams/GSW/2026.html"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }

    req = httpx.get(url, headers=headers)
    
    # Uncomment hidden tables
    uncommented = re.sub(r'<!--(.*?)-->', r'\1', req.text, flags=re.DOTALL)
    html = BeautifulSoup(uncommented, "lxml")

    advanced_table = html.find("table", id="advanced")
    
    df = pd.read_html(str(advanced_table))[0]
    df = df[df["Player"] != "Team Totals"].reset_index(drop=True)
    df = df[["Player", "WS", "WS/48", "BPM"]]
    
    return df

print(getStartingElo())

