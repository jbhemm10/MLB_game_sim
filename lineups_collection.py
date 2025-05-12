"""
This file contains the function to collect the starting lineups for a given date
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import pytz

# === FETCH MLB SCHEDULE ===
async def get_mlb_games(date: str):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Error fetching schedule: {response.status}")
            data = await response.json()

    if not data.get('dates'):
        return []

    return data['dates'][0]['games']

# === FETCH LINEUP FOR ONE GAME ===
async def fetch_lineup(session, gamePk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live"

    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Warning: Failed to fetch lineup for {gamePk} (status {response.status})")
                return (gamePk, None)

            data = await response.json()

            home_team = data['gameData']['teams']['home']['name']
            away_team = data['gameData']['teams']['away']['name']

            # NEW: pull players from boxscore
            boxscore = data['liveData']['boxscore']['teams']

            home_lineup = []
            for player_id, player_info in boxscore['home']['players'].items():
                if 'battingOrder' in player_info:
                    home_lineup.append({
                        "player_name": player_info['person']['fullName'],
                        "player_id": player_info['person']['id'],
                        "batting_order": player_info['battingOrder']
                    })

            away_lineup = []
            for player_id, player_info in boxscore['away']['players'].items():
                if 'battingOrder' in player_info:
                    away_lineup.append({
                        "player_name": player_info['person']['fullName'],
                        "player_id": player_info['person']['id'],
                        "batting_order": player_info['battingOrder']
                    })

            # Sort by batting order (1, 2, 3...9)
            home_lineup.sort(key=lambda x: int(x['batting_order']))
            away_lineup.sort(key=lambda x: int(x['batting_order']))

            return (gamePk, {
                "home_team": home_team,
                "away_team": away_team,
                "home_lineup": home_lineup,
                "away_lineup": away_lineup
            })

    except Exception as e:
        print(f"Error fetching lineup for gamePk {gamePk}: {e}")
        return (gamePk, None)

# === MASTER COLLECTOR ===
async def collect_full_lineup(date: str):
    games = await get_mlb_games(date)
    if not games:
        print(f"No games found for {date}")
        return []

    gamePks = [game['gamePk'] for game in games]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_lineup(session, gamePk) for gamePk in gamePks]
        lineups_data = await asyncio.gather(*tasks)

    full_lineups = []
    for gamePk, lineup in lineups_data:
        if lineup is None:
            continue  # Skip games with no valid lineup
        full_lineups.append(lineup)

    return full_lineups

# === SAVING FUNCTION ===
def save_lineups_to_json(lineup_list, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(lineup_list, f, indent=4)
    print(f"Saved {len(lineup_list)} lineups to {filename}")

# === PUBLIC CALLABLE FUNCTION ===
def get_lineups_for_date(date: str, save_to_file: bool = True):
    lineups = asyncio.run(collect_full_lineup(date))

    if save_to_file and lineups:
        filename = f"lineups_data/lineups_on_{date}.json"
        save_lineups_to_json(lineups, filename)

    return lineups

