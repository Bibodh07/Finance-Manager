import numpy as np
import pandas as pd
import json


elo_df = pd.read_json('elo_data.json')

elo_df["ws"]       = elo_df["ws"].astype(float)
elo_df["ws_per48"] = elo_df["ws_per48"].astype(float)
elo_df["bpm"]      = elo_df["bpm"].astype(float)

# compute raw score
elo_df["raw_score"] = (
    (elo_df["ws"] * 0.3) +
    (elo_df["ws_per48"] * 100 * 0.3) +
    (elo_df["bpm"] * 0.4)
)

# normalize to 1200-1800
min_score = elo_df["raw_score"].min()
max_score = elo_df["raw_score"].max()

elo_df["elo"] = 1200 + ((elo_df["raw_score"] - min_score) / (max_score - min_score)) * 600

# sort by elo
elo_df = elo_df.sort_values("elo", ascending=False).reset_index(drop=True)


# check how correlated the stats are with EACH OTHER
print("WS vs BPM:",      np.corrcoef(elo_df["ws"],       elo_df["bpm"])[0][1])
print("WS vs WS/48:",    np.corrcoef(elo_df["ws"],       elo_df["ws_per48"])[0][1])
print("WS/48 vs BPM:",   np.corrcoef(elo_df["ws_per48"], elo_df["bpm"])[0][1])
