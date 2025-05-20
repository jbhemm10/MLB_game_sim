"""
This script is the master file for the simulation. It calls all of the neccessary functions
to properly run the simulation.
INPUTS:
- Hitting and pitching data from MLB Savant for the current year
- Game information for the current date
OUTPUTS:
- CSV files containing the data for hitters and pitchers
- JSON file containing game information including teams, pitchers, venue, and game time

"""

#Import the necessary libraries
import pandas as pd
import datetime
import pytz
import os

#Import the necessary modules
import player_data_collection
from games_collection import get_games_for_date
from lineups_collection import get_lineups_for_date
import merge_hitters
from simulation import simulate_matchups
from analysis import get_yesterdays_scores
from analysis import simulation_analysis

# Set the current year
current_year = datetime.datetime.now().year

# Set the current date
current_date = datetime.datetime.now().date()

# Run data collection for hitters and pitchers
player_data_collection.download_hitters_data()
player_data_collection.download_pitchers_data()

# Show the headers and first 5 rows of the hitters data 
hitters_data = pd.read_csv(f'player_data/{current_year}_hitters_data.csv')
print(hitters_data.head())

# Show the headers and first 5 rows of the pitchers data
pitchers_data = pd.read_csv(f'player_data/{current_year}_pitchers_data.csv')
print(pitchers_data.head())

# Collect games for the current date
date = current_date.strftime("%Y-%m-%d")
games = get_games_for_date(date, save_to_file=True)

# Print the games to verify
for game in games:
        print(f"{game['away_team']} ({game['away_pitcher']})  at {game['home_team']} ({game['home_pitcher']}) - {game['venue']} - {game['game_time_et']}")

# Collect lineups for the current date
lineups = get_lineups_for_date(date, save_to_file=True)

# Print the lineups to verify
for lineup in lineups:
        print(f"{lineup['home_team']} vs {lineup['away_team']}")
        print(f"{lineup['home_team']} Lineup:")
        for player in lineup['home_lineup']:
            print(f"  {player['player_name']} (ID: {player['player_id']})")
        print(f"{lineup['away_team']} Lineup:")
        for player in lineup['away_lineup']:
            print(f"  {player['player_name']} (ID: {player['player_id']})")

# Merge the hitters data with the lineups data 
merged_data = merge_hitters.merge_offensive_data(date)

# Replace missing values with 0
merged_data.fillna(0, inplace=True)

# Print the merged data to verify
print(merged_data.head())

# Save the merged data to a CSV file
os.makedirs("merged_data", exist_ok=True)
merged_data.to_csv(f"merged_data/{date}_merged_data.csv", index=False)

# Run the simulation
simulated_games = simulate_matchups(num_simulations=10000)
os.makedirs("simulated_games", exist_ok=True)
simulated_games.to_csv(f"simulated_games/simulated_games_{date}.csv", index=False)

# Get yesterday's scores
yesterday_scores = get_yesterdays_scores()

# Run the simulation analysis
simulation_analysis()



