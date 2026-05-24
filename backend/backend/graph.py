import json
import pandas as pd
import numpy as np


def generateEloGraph():

    with open("elo.json") as f:
        elo_dict = json.load(f)

    elo_df = pd.DataFrame(list(elo_dict.items()), columns=["team", "elo"])
    eloGraph = np.array(elo_df["elo"])
    teamNames = np.arange(len(elo_df["team"]))
    return np.polyfit(teamNames, eloGraph, 1)
   

    
def getTrendLineData():

    teams = []
    
    with open("elo_ratings.txt", "r") as f:
        for text in f:

            text = text.split()
            
            try:
                teams.append(text[1])
     
            except:
                continue
        

    slope, coeff = generateEloGraph()
    


    data = [{
        "team": teams[i],
        "trend": float(round((slope * i) + coeff, 2))
    } for i in range(30)]


    return data
    



getTrendLineData()
