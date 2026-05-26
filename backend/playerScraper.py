from bs4 import BeautifulSoup
import httpx
import regex as re
from dotenv import load_dotenv, find_dotenv
import psycopg2
import os
import time
import random

load_dotenv(find_dotenv())



conn = psycopg2.connect(
    dbname=os.getenv("data_base"),
    user=os.getenv("dbuser"),
    password=os.getenv("dbpassword"),
    host=os.getenv("dbhost"),
    port=int(os.getenv("dbport"))
)

def clean(val):
    
    if val is None or val == "":
        print(val)
        return None
    return val

def parse_table(html, table_id):
    table = html.find("table", id=table_id)
    if not table:
        return {}
    result = {}
    print(table)
    for row in table.find_all("tr"):
        name_td = row.find("td", {"data-stat": "name_display"})
        if not name_td:
            continue
        name = name_td.get_text(strip=True)
        result[name] = {td["data-stat"]: td.get_text(strip=True)
                        for td in row.find_all("td") if td.get("data-stat")}
    return result


def parse_injuries(html):
    table = html.find("table", id="injuries")
    if not table:
        return []
    players = []
    for row in table.find_all("tr"):
        name_th = row.find("th", {"data-stat": "player"})
        team_td = row.find("td", {"data-stat": "team_name"})
        note_td = row.find("td", {"data-stat": "note"})
        
        if not name_th or not team_td or not note_td:  # skip header rows
            continue
            
        players.append({
            "name":   name_th.get_text(strip=True),
            "team":   team_td.get_text(strip=True),
            "status": note_td.get_text(strip=True)
        })
    return players
        
        


def getPlayerData(teamCode):
    url = f"https://www.basketball-reference.com/teams/{teamCode}/2026.html"
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






    totals   = parse_table(html, "totals_stats")
    advanced = parse_table(html, "advanced")
    pbp      = parse_table(html, "pbp_stats")
    adj      = parse_table(html, "adj_shooting")

    players = []
    for name in totals:
        t = totals.get(name, {})
        a = advanced.get(name, {})
        p = pbp.get(name, {})
        s = adj.get(name, {})

        players.append({
            "name":   name,
            "team":   teamCode,
            "pts":    t.get("pts"),
            "ast":    t.get("ast"),
            "reb":    t.get("trb"),
            "tov":    t.get("tov"),
            "stl":    t.get("stl"),
            "blk":    t.get("blk"),
            "fga":    t.get("fga"),
            "efg":    t.get("efg_pct"),
            "games":  t.get("games"),
            "ws":     a.get("ws"),
            "vorp":   a.get("vorp"),
            "pmon":   p.get("plus_minus_on"),
            "pmnet":  p.get("plus_minus_net"),
            "ts_pts": s.get("ts_pts_added"),
        })

    return players


def save_to_db(player):
    cursor = conn.cursor()
  
    try:
        cursor.execute(
            """
            INSERT INTO playerDB (name, team, games, pts, ast, reb, tov, stl, blk, fga, efg, ws, vorp, pmon, pmnet, ts_pts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                clean(player["name"]),
                clean(player["team"]),
                clean(player["games"]),
                clean(player["pts"]),
                clean(player["ast"]),
                clean(player["reb"]),
                clean(player["tov"]),
                clean(player["stl"]),
                clean(player["blk"]),
                clean(player["fga"]),
                clean(player["efg"]),
                clean(player["ws"]),
                clean(player["vorp"]),
                clean(player["pmon"]),
                clean(player["pmnet"]),
                clean(player["ts_pts"])
            )
        )
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def save_injury_to_db(player):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO injuries (playerName, teamName, note)
            VALUES (%s, %s, %s)
            """,
            (
                player["name"],
                player["team"],
                player["status"]
            )
        )
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()





def helper_getEveryTeam(player):
    save_to_db(player)


def getEveryTeam():
    NBA_TEAMS = [
        "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
        "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
        "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
    ]

    failed = []

    for team in NBA_TEAMS:
        try:
            print(f"Collecting team data {team}")
            players = getPlayerData(team)
            for player in players:
                helper_getEveryTeam(player)
            time.sleep(random.uniform(8, 15))
        except Exception as e:
            print(f"Failed team {team} because of {e}")
            failed.append(team)

    while failed:
        print("retrying...")
        retry = failed.copy()
        for team in retry:
            try:
                print(f"Collecting team data {team}")
                players = getPlayerData(team)
                for player in players:
                    helper_getEveryTeam(player)
                failed.remove(team)
                time.sleep(random.uniform(8, 15))
            except Exception as e:
                print(f"Failed and retrying team {team} because of {e}")
                continue


def getInjuredPlayers():
    url = "https://www.basketball-reference.com/friv/injuries.fcgi"
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

    players =  parse_injuries(html)

    for player in players:
        save_injury_to_db(player)


print(getInjuredPlayers())

conn.commit()
conn.close()