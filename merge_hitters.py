"""
This script merges the lineups data with the hitters data for a given date.
INPUTS:
- .json file containing the lineups for a specific date
- .csv file containing the hitters data for the current year
OUTPUTS:
- A DataFrame containing the merged data with player information, team, side (home/away), and hitting statistics.
"""

from hitter_splits_collection import get_player_splits

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
    hitters_data = pd.read_csv('2025_hitter_split_stats.csv')
    sprint_speed_data = pd.read_csv(f'player_data/{year}_hitters_data.csv')

    # Merge the sprint speed data with hitters data
    hitters_data = pd.merge(hitters_data, sprint_speed_data[['player_id', 'sprint_speed']], on='player_id', how='left')

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

    # Check to see if players_df has player_ids
    if players_df.empty:
        print("No player IDs can be found in the lineups data. " \
        "Today's lineups most likely have not been released yet.")
    else:
        # Merge the data if available
        merged_data = pd.merge(players_df, hitters_data, on='player_id', how='left')

        # Return the merged data
        return merged_data
        




