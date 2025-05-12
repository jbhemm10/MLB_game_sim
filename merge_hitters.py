"""
This script merges the lineups data with the hitters data for a given date.
INPUTS:
- .json file containing the lineups for a specific date
- .csv file containing the hitters data for the current year
OUTPUTS:
- A DataFrame containing the merged data with player information, team, side (home/away), and hitting statistics.
"""

import json
import pandas as pd
import datetime

import pandas as pd

def merge_offensive_data(date):
    # Set date and year
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    year = datetime.datetime.now().year

    # Load your lineups
    lineups_df = pd.read_json(f"lineups_data/lineups_on_{date}.json")

    # Load your hitters data
    hitters_data = pd.read_csv(f"player_data/{year}_hitters_data.csv")

    # Step 1: Flatten the lineups
    players_list = []

    for idx, row in lineups_df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        game_id = row['game_id']

        for player in row['home_lineup']:
            players_list.append({
                "team": home_team,
                "side": "home",
                "player_name": player['player_name'],
                "player_id": player['player_id'],
                "game_id": game_id
            })

        for player in row['away_lineup']:
            players_list.append({
                "team": away_team,
                "side": "away",
                "player_name": player['player_name'],
                "player_id": player['player_id'],
                "game_id": game_id
            })

    # Now we have a nice players DataFrame
    players_df = pd.DataFrame(players_list)

    # Step 2: Merge with hitters data
    merged_data = pd.merge(players_df, hitters_data, on='player_id', how='left')

    return merged_data




