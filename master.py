# Master python file to run all of the functions created in the other files

#Import the necessary libraries
import pandas as pd
import datetime

#Import the necessary modules
import data_collection
from games_collection import get_games_for_date

# Set the current year
current_year = datetime.datetime.now().year

# Set the current date
current_date = datetime.datetime.now().date()

# Run data collection for hitters and pitchers
data_collection.download_hitters_data()
data_collection.download_pitchers_data()

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
    print(f"{game['away_team']} ({game['away_pitcher']}) at {game['home_team']} ({game['home_pitcher']}) - {game['venue']} - {game['game_time_et']}")