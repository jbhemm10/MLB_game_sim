import requests
import pandas as pd

# MLB stats endpoint for vs. LHP (default: 2024 season, hitters, qualified)
url = "https://www.mlb.com/stats/"

# MLB uses JavaScript to render the table, so we use the underlying data endpoint instead
api_url = "https://baseballsavant.mlb.com/proxy/api/stats/player"

params = {
    "statType": "season",
    "playerPool": "ALL",
    "position": "",
    "team": "",
    "league": "",
    "season": "2024",
    "gameType": "R",
    "split": "vl",  # vs Left-Handed Pitchers
    "min": "q",     # Qualified players
    "sortStat": "avg",
    "order": "desc"
}

r = requests.get(api_url, params=params)
data = r.json()

# Convert to DataFrame
df = pd.DataFrame(data['stats'])
print(df.head())

df.to_csv("mlb_vsL_2024.csv", index=False)