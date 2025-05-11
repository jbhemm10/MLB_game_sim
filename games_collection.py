""" 
This script collects MLB game information for a given date
INPUTS:
- Date in the format YYYY-MM-DD
OUTPUTS:
- JSON file containing game information including teams, pitchers, venue, and game time

The JSON file is saved in a folder named "gameday_data" with the date as part of the filename
"""

# Import necessary libraries
import asyncio
import aiohttp
import json
import os
from datetime import datetime
import pytz

# === STEP 1: Get games scheduled for a given date ===
async def get_mlb_games(date: str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Error fetching schedule: {response.status}")
            data = await response.json()

    if not data.get('dates'):
        return []

    games = data['dates'][0]['games']
    return games

# === STEP 2: For each gamePk, get the probable pitchers and their IDs ===
async def fetch_gamefeed(session, gamePk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live"

    async with session.get(url) as response:
        if response.status != 200:
            print(f"Warning: Error fetching game feed for {gamePk}: {response.status}")
            return (gamePk, "TBD", "TBD", None, None)  # Return None for IDs if there is an error

        data = await response.json()

        # Get the probable pitchers and their IDs
        home_pitcher_data = data['gameData']['probablePitchers'].get('home', {})
        away_pitcher_data = data['gameData']['probablePitchers'].get('away', {})

        # Home pitcher
        home_pitcher_name = home_pitcher_data.get('fullName', 'TBD')
        home_pitcher_id = home_pitcher_data.get('id', None)  # ID for Baseball Savant

        # Away pitcher
        away_pitcher_name = away_pitcher_data.get('fullName', 'TBD')
        away_pitcher_id = away_pitcher_data.get('id', None)  # ID for Baseball Savant

        return (gamePk, home_pitcher_name, away_pitcher_name, home_pitcher_id, away_pitcher_id)

# === STEP 3: Master function to collect full game info ===
async def collect_full_game_info(date: str):
    games = await get_mlb_games(date)
    if not games:
        print(f"No games found for {date}")
        return []

    gamePks = [game['gamePk'] for game in games]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_gamefeed(session, gamePk) for gamePk in gamePks]
        pitchers_data = await asyncio.gather(*tasks)

    pitchers_lookup = {pk: (home_p, away_p, home_id, away_id) for pk, home_p, away_p, home_id, away_id in pitchers_data}

    # Set Eastern Timezone (US/Eastern)
    eastern = pytz.timezone('US/Eastern')

    full_game_list = []
    for game in games:
        gamePk = game['gamePk']
        home_team = game['teams']['home']['team']['name']
        away_team = game['teams']['away']['team']['name']
        venue = game['venue']['name']
        game_time_utc = game['gameDate']  # Game time in UTC

        # Convert UTC to Eastern Time
        if game_time_utc:
            game_time_utc = datetime.strptime(game_time_utc, "%Y-%m-%dT%H:%M:%SZ")
            game_time_utc = pytz.utc.localize(game_time_utc)  # Make the time timezone-aware
            game_time_et = game_time_utc.astimezone(eastern)  # Convert to Eastern Time
            game_time_et_str = game_time_et.strftime("%Y-%m-%d %I:%M %p %Z")  # Format the time
        else:
            game_time_et_str = "Unknown"

        home_pitcher, away_pitcher, home_pitcher_id, away_pitcher_id = pitchers_lookup.get(gamePk, ("TBD", "TBD", None, None))

        game_info = {
            "home_team": home_team,
            "away_team": away_team,
            "home_pitcher": home_pitcher,
            "away_pitcher": away_pitcher,
            "home_pitcher_id": home_pitcher_id,  # Pitcher ID for Baseball Savant
            "away_pitcher_id": away_pitcher_id,  # Pitcher ID for Baseball Savant
            "venue": venue,
            "game_time_et": game_time_et_str,  # Eastern Time
            "gamePk": gamePk
        }
        full_game_list.append(game_info)

    return full_game_list

# === STEP 4: Saving function (optional) ===
def save_games_to_json(game_list, date: str):
    # Create 'gameday_data' folder if it doesn't exist
    os.makedirs("gameday_data", exist_ok=True)

    # Set the filename with the date
    filename = f"gameday_data/games_on_{date}.json"

    # Save to the file
    with open(filename, "w") as f:
        json.dump(game_list, f, indent=4)
    print(f"Saved {len(game_list)} games to {filename}")

# === RUNNER FUNCTION ===
def get_games_for_date(date: str, save_to_file: bool = True):
    games = asyncio.run(collect_full_game_info(date))

    if save_to_file and games:
        save_games_to_json(games, date)

    return games
