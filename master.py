# Master python file to run all of the functions created in the other files

#Import the necessary libraries
import pandas as pd
import datetime

#Import the necessary modules
import data_collection

# Set the current year
current_year = datetime.datetime.now().year

# Run data collection for hitters and pitchers
data_collection.download_hitters_data()
data_collection.download_pitchers_data()

#Show the collected data 
hitters_data = pd.read_csv(f'player_data/{current_year}_hitters_data.csv')
print(hitters_data.head())

pitchers_data = pd.read_csv(f'player_data/{current_year}_pitchers_data.csv')
print(pitchers_data.head())