import numpy as np
import pandas as pd
import json

elo_df = pd.read_json('elo_data.json')

elo_df["ws"]       = elo_df["ws"].astype(float)
elo_df["ws_per48"] = elo_df["ws_per48"].astype(float)
elo_df["bpm"]      = elo_df["bpm"].astype(float)
elo_df["srs"]      = elo_df["srs"].astype(float)

# check SRS correlation with existing stats first
print("SRS vs WS:",      np.corrcoef(elo_df["srs"], elo_df["ws"])[0][1])
print("SRS vs WS/48:",   np.corrcoef(elo_df["srs"], elo_df["ws_per48"])[0][1])
print("SRS vs BPM:",     np.corrcoef(elo_df["srs"], elo_df["bpm"])[0][1])

# compute raw score with SRS
elo_df["raw_score"] = (
    (elo_df["ws"]       * 0.2) +
    (elo_df["ws_per48"] * 100 * 0.2) +
    (elo_df["bpm"]      * 0.3) +
    (elo_df["srs"]      * 0.3)
)

# normalize to 1200-1800
min_score = elo_df["raw_score"].min()
max_score = elo_df["raw_score"].max()

elo_df["elo"] = 1200 + ((elo_df["raw_score"] - min_score) / (max_score - min_score)) * 600

# sort by elo
elo_df = elo_df.sort_values("elo", ascending=False).reset_index(drop=True)

# human readable
with open("elo_ratings.txt", "w") as f:
    f.write(f"{'Rank':<6}{'Team':<35}{'Elo':<10}\n")
    f.write("-" * 51 + "\n")
    for i, row in elo_df.iterrows():
        f.write(f"{i+1:<6}{row['team']:<35}{row['elo']:.2f}\n")

# for the simulator
elo_dict = dict(zip(elo_df["team"], elo_df["elo"]))
with open("elo.json", "w") as f:
    json.dump(elo_dict, f, indent=4)