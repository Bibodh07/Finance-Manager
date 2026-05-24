import httpx
import pandas as pd
import re
from bs4 import BeautifulSoup, Comment

def getStartingElo_regex():
    url = "https://www.basketball-reference.com/teams/GSW/2026.html"
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
    table = html.find("table", id="advanced")
    df = pd.read_html(str(table))[0]
    df = df[df["Player"] != "Team Totals"].reset_index(drop=True)
    df = df[["Player", "WS", "WS/48", "BPM"]]
    return df

def getStartingElo_comment():
    url = "https://www.basketball-reference.com/teams/GSW/2026.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }
    req = httpx.get(url, headers=headers)
    html = BeautifulSoup(req.text, "lxml")
    comments = html.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        inner = BeautifulSoup(str(comment), "lxml")
        table = inner.find("table", id="advanced")
        if table:
            df = pd.read_html(str(table))[0]
            df = df[df["Player"] != "Team Totals"].reset_index(drop=True)
            df = df[["Player", "WS", "WS/48", "BPM"]]
            return df
        
def getSRS(teamName: str) -> float:
    url = f"https://www.basketball-reference.com/teams/{teamName}/2026.html"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }
    req = httpx.get(url, headers=headers)
    html = BeautifulSoup(req.text, "lxml")

    # find the anchor tag that links to SRS glossary
    srs_tag = html.find("a", href="/about/glossary.html#srs")
    
    # get the parent p tag text and extract the number
    srs_text = srs_tag.parent.parent.get_text()
    srs_value = srs_text.split(":")[1].strip().split()[0]
    
    return {"team": teamName, "srs": float(srs_value)}

print(getSRS("GSW"))
        
   
       
            



