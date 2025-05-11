""""
This script downloads hitting and pitching data from MLB Savant for the current year. 
INPUTS: 
- Hitting statistics including various "basic" and "advanced" metrics from Baseball Savant.
- Pitching statistics including various "basic" and "advanced" metrics from Baseball Savant.
OUTPUTS:
- CSV files containing the data for hitters and pitchers.

# The data is saved in a folder named "player_data" with the current year as part of the filename.
"""

# Import necessary libraries
import requests
import datetime
import os
# Download hitting data from MLB Savant from the current year
def download_hitters_data(save_path=None):

    # Get the current year
    current_year = datetime.datetime.now().year 

    # Create player_data folder if it doesn't exist
    os.makedirs("player_data", exist_ok=True)

    if save_path is None:
        save_path = f'player_data/{current_year}_hitters_data.csv'

    # This is the URL for the MLB Savant leaderboard for hitters
    # The number of minimum plate appearances is set to 10
    # The selections include various hitting statistics like avg, slg, wOBA, etc.
    url = (f'https://baseballsavant.mlb.com/leaderboard/custom?year={current_year}&type=batter&filter=&min=10&'
           'selections=player_age,ab,pa,hit,single,double,triple,home_run,strikeout,walk,k_percent,'
           'bb_percent,batting_avg,slg_percent,on_base_percent,on_base_plus_slg,xba,xslg,woba,xwoba'
           '&sort=xwoba&sortDir=desc&csv=true')

    response = requests.get(url)

    # Check if the request was successful
    # If the request was successful, save the content to a file
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Leaderboard for {current_year} downloaded and saved to {save_path}")
    else:
        print(f"Failed to download data. Status code: {response.status_code}")

# Downloading pitchers data from MLB Savant for the current year
def download_pitchers_data(save_path=None):
    
    # Get the current year
    current_year = datetime.datetime.now().year

    if save_path is None:
        save_path = f'player_data/{current_year}_pitchers_data.csv'

    # This is the URL for the MLB Savant leaderboard for pitchers
    # The number of minimum plate appearances is set to 10
    # The selections include various pitching statistics like ERA, xwOBA, whiff percentage, etc.
    url = (f'https://baseballsavant.mlb.com/leaderboard/custom?year={current_year}&type=pitcher&filter=&min=10&'
           'selections=player_age,p_game,p_formatted_ip,pa,ab,hit,single,double,triple,home_run,'
           'strikeout,walk,k_percent,bb_percent,batting_avg,slg_percent,on_base_percent,'
           'on_base_plus_slg,p_era,p_opp_batting_avg,xba,xslg,woba,xwoba,whiff_percent,swing_percent'
           '&sort=xwoba&sortDir=asc&csv=true')

    response = requests.get(url)

    # Check if the request was successful
    # If the request was successful, save the content to a file
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Pitcher leaderboard for {current_year} downloaded and saved to {save_path}")
    else:
        print(f"Failed to download data. Status code: {response.status_code}")