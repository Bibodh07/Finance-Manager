from bs4 import BeautifulSoup
import httpx
import json
import regex as re
import pandas as pd
import time




def getPlayerData(teamCode):

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

    totals_table = html.find("table", id="totals_stats")
    advanced_table = html.find("table", id="advanced")
    pbp = html.find("table", id="pbp_stats")

    tableRows = totals_table.find_all("tr")
    ad_rows = advanced_table.find_all("tr")
    pbp_rows = advanced_table.find_all("tr")

    stat = {
         "pts":0,
         "ast":0,
         "reb":0,
         "tov":0,
         "stl":0,
         "blk":0,
         "fgs":0,
         "efgs":0,
         "games":0,
         "ws":0,
         "vorp":0,
         "pmon":0,
         "pmnet":0
    }

  

    

  
    for data in tableRows:
      
        try:     
            pts = data.find("td", {"data-stat":"pts"}).get_text()
            ast = data.find("td", {"data-stat":"ast"}).get_text()
            rb = data.find("td", {"data-stat" : "trb"}).get_text()
            To = data.find("td", {"data-stat":"tov"}).get_text()
            stl = data.find("td", {"data-stat":"stl"}).get_text()
            blk = data.find("td", {"data-stat":"blk"}).get_text()
            fgs = data.find("td", {"data-stat":"fga"}).get_text()
            efgs = data.find("td", {"data-stat":"efg_pct"}).get_text()
            games = data.find("td", {"data-stat":"games"}).get_text()

            print(pts)

            stat["pts"] = pts
            stat["ast"] = ast
            stat["reb"] = rb
            stat["tov"] = To
            stat["stl"] = stl
            stat["blk"] = blk
          

         
                
        except Exception as e:
            print(e)
            continue


    

    
    for data in ad_rows:
            try:
                ws = data.find("td", {"data-stat":"ws"}).get_text()
                vorp = data.find("td", {"data-stat":"vorp"}).get_text()
            except:
                continue

            stat["ws"] = ws
            stat["vorp"] = vorp


    
    for data in pbp:

            try:
                pmon = data.find("td", {"data-stat":"plus_minus_on"}).get_text()
                pmnet = data.find("td", {"data-stat":"plus_minus_net"}).get_text()
            except:
                continue

            stat["pmon"] = pmon
            stat["pmnet"] = pmnet
            print(stat)



    

    return stat


   





print(getPlayerData("GSW"))