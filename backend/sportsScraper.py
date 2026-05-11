from bs4 import BeautifulSoup
import httpx
import json
import regex as re
import pandas as pd
import time


NBA_TEAMS = [
    "ATL", "BOS", "BRK", "CHO", "CHI",
    "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM",
    "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHO", "POR",
    "SAC", "SAS", "TOR", "UTA", "WAS"
]




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



def getStartingElo(teamName: str):
    url = f"https://www.basketball-reference.com/teams/{teamName}/2026.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }

    req = httpx.get(url, headers=headers)
    uncommented = re.sub(r'<!--(.*?)-->', r'\1', req.text, flags=re.DOTALL)
    html = BeautifulSoup(uncommented, "lxml")

    # advanced table
    advanced_table = html.find("table", id="advanced")

    # SRS from meta div
    srs_tag = html.find("a", href="/about/glossary.html#srs")
    srs_value = srs_tag.parent.parent.get_text().split(":")[1].strip().split()[0]

    stats = {
        "team":     teamName,
        "ws":       advanced_table.find_all("td", {"data-stat": "ws"})[-1].get_text(),
        "ws_per48": advanced_table.find_all("td", {"data-stat": "ws_per_48"})[-1].get_text(),
        "bpm":      advanced_table.find_all("td", {"data-stat": "bpm"})[-1].get_text(),
        "srs":      float(srs_value)
    }

    return stats

def retryFailed(failed: list, results: list) -> list:
    for team in failed:
        if any(r["team"] == team for r in results):
            continue
        try:
            print(f"Retrying {team}...")
            data = getStartingElo(team)
            results.append(data)
            with open("elo_data.json", "w") as f:
                json.dump(results, f, indent=4)
            time.sleep(15)
        except Exception as e:
            print(f"Failed again on {team}: {e}")
    return results


def getAllTeamsElo() -> list[dict]:
    results = []
    failed = []

    try:
        with open("elo_data.json", "r") as f:
            results = json.load(f)
            print(f"Loaded {len(results)} existing teams from file")
    except FileNotFoundError:
        pass

    for team in NBA_TEAMS:
        if any(r["team"] == team for r in results):
            print(f"Skipping {team}, already scraped")
            continue
        try:
            print(f"Scraping {team}...")
            data = getStartingElo(team)
            results.append(data)
            with open("elo_data.json", "w") as f:
                json.dump(results, f, indent=4)
            time.sleep(4)
        except Exception as e:
            print(f"Failed on {team}: {e}")
            failed.append(team)
            continue

    return results, failed


results, failed = getAllTeamsElo()
print(f"\nScraped {len(results)}/30 teams")
print(f"Failed: {failed}")

if failed:
    results = retryFailed(failed, results)
    print(f"\nFinal: {len(results)}/30 teams")

