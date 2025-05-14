"""
This script runs a simulation for each matchup in the MLB for a given date. The simulation runs
through 100,000 iterations and calculates the probability of each team winning based on the hitters
statistics.  

INPUTS:
- Hitters statistics from the associated merged_data.csv file for the current date

OUTPUTS:
- A CSV file containing the simulation results for each matchup
- 
"""

# Import the necessary libraries   
import pandas as pd
import numpy as np
import datetime
import random
from collections import defaultdict
from tqdm import tqdm

# Set current date
date = datetime.datetime.now().date()

def simulate_matchups(num_simulations = 10000):
    
    # Load the merged data
    data = pd.read_csv(f'merged_data/{date}_merged_data.csv')

    # Group players by game and side
    grouped_data = data.groupby(['game_id', 'side'])
    games = {}

    for (game_id, side), group in grouped_data:
        players = group.to_dict(orient='records')
        for p in players:
            pa = p['pa'] if p['pa'] > 0 else 1
            ab = p['ab'] if p['ab'] > 0 else 1
            p['walk_rate'] = p['walk'] / pa  if p['walk']/ pa > 0 else 0.07
            p['single_rate'] = p['single'] / ab if p['single']/ ab > 0 else 0.2
            p['double_rate'] = p['double'] / ab if p['double']/ ab > 0 else 0.1
            p['triple_rate'] = p['triple'] / ab if p['triple']/ ab > 0 else 0.05
            p['home_run_rate'] = p['home_run'] / ab if p['home_run']/ ab > 0 else 0.1
        if game_id not in games:
            games[game_id] = {}
        games[game_id][side] = players

    def simulate_at_bat(player):
        r =random.randint(0,1000)/1000
        if r > player['walk_rate']:
            r = random.randint(0,1000)/1000
            if r < player['single_rate']:
                return "single"
            elif player['single_rate'] < r < player['single_rate'] + player['double_rate']:
                return "double"
            elif player['single_rate'] + player['double_rate'] < r < player['single_rate'] + player['double_rate'] + player['triple_rate']:
                return "triple"
            elif player['single_rate'] + player['double_rate'] + player['triple_rate'] < r < player['single_rate'] + player['double_rate'] + player['triple_rate'] + player['home_run_rate']:
                return "home_run"
            else:
                return "out"
        else:
            return "walk"
    
    def simulate_half_inning(lineup, start_idx = 0):

        # Initialize the outs, bases, runs, and index (batter lineup position)
        outs = 0
        bases = [None, None, None]
        runs = 0
        idx = start_idx

        while outs < 3:
            batter = lineup[idx % len(lineup)]
            
            # Get a random number for runner's likelihood of running additional bases
            base_run = random.randint(0,100)

            # Simulate the at-bat using the prior function
            result = simulate_at_bat(batter)
            
            # Sacrifice fly
            if result == "out" and bases[2] is not None and outs < 2:
                runs += 1
                bases[2] = None
                outs += 1
            # Batter gets out
            elif result == "out":
                outs += 1
            # Batter hits a single
            elif result == "single":
                if bases[2] is not None:
                    runs += 1
                bases[2] = bases[1]
                bases[1] = bases[0]
                bases[0] = batter
            # Batter hits a double
            elif result == "double":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                bases[2] = bases[0]
                bases[1] = batter
                bases[0] = None     
            # Batter hits a triple
            elif result == "triple":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                if bases[0] is not None:
                    runs += 1
                bases[2] = batter
                bases[1] = None
                bases[0] = None
            # Batter hits a home run
            elif result == "home_run":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                if bases[0] is not None:
                    runs += 1
                runs += 1
                bases[2] = None
                bases[1] = None
                bases[0] = None
            # Batter draws a walk
            elif result == "walk":
                if bases[0]:
                    if bases[1]:
                        if bases[2]:
                            runs += 1
                        bases[2] = bases[1]
                    bases[1] = bases[0]
                bases[0] = batter

            # Move to the next batter
            idx += 1
        # Return the number of runs scored and the index of the next batter
        return runs, idx % len(lineup)
    
    # Function to simulate an extra inning
    # This function is called when the game is tied after 9 innings
    def simulate_extra_inning(lineup, idx):
        previous_batter = simulate_at_bat(lineup[idx % len(lineup) -1])
        outs = 0
        bases = [None, previous_batter, None]
        runs = 0

        while outs < 3:
            batter = lineup[idx % len(lineup)]
            result = simulate_at_bat(batter)

            # Batter hits a sacrifice fly
            if result == "out" and bases[2] is not None and outs < 2:
                runs += 1
                outs += 1
            # Batter gets out
            elif result == "out":
                outs += 1
            # Batter hits a single
            elif result == "single":
                if bases[2] is not None:
                    runs += 1
                bases[2] = bases[1]
                bases[1] = bases[0]
                bases[0] = batter 
            # Batter hits a double
            elif result == "double":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                bases[2] = bases[0]
                bases[1] = batter
                bases[0] = None
            # Batter hits a triple
            elif result == "triple":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                if bases[0] is not None:
                    runs += 1
                bases[2] = batter
                bases[1] = None
                bases[0] = None
            # Batter hits a home run
            elif result == "home_run":
                if bases[2] is not None:
                    runs += 1
                if bases[1] is not None:
                    runs += 1
                if bases[0] is not None:
                    runs += 1
                runs += 1
                bases[2] = bases[1] = bases[0] = None
            # Batter draws a walk
            elif result == "walk":
                if bases[0]:
                    if bases[1]:
                        if bases[2]:
                            runs += 1
                        bases[2] = bases[1]
                    bases[1] = bases[0]
                bases[0] = batter

            # Move to the next batter
            idx += 1
        # Return the number of runs scored and the index of the next batter
        return runs, idx % len(lineup)

    # Function to simulate a game
    def simulate_game(team_home, team_away):
        # Initialize the scores and indices for both teams
        home_score = away_score = 0
        home_idx = away_idx = 0

        # Simulate 9 innings of play
        for inning in range(9):
            # Simulate the away half of the inning
            away_score, away_idx = simulate_half_inning(team_away, away_idx)
            away_score += away_score
            # Simulate the home half of the inning
            home_score, home_idx = simulate_half_inning(team_home, home_idx)
            home_score += home_score
        
        # If the game is tied after 9 innings, go to extra innings
        if home_score == away_score:
            inning = 9
            while home_score == away_score:
                # Simulate the away half of the inning
                away_score, away_idx = simulate_extra_inning(team_away, away_idx)
                away_score += away_score
                # Simulate the home half of the inning
                home_score, home_idx = simulate_extra_inning(team_home, home_idx)
                home_score += home_score
                inning += 1
        
        return home_score, away_score
    
    # Initialize a dictionary to store the results
    results = []

    # Simulate each game
    for game_id, teams in tqdm(games.items(), desc="Simulating games", unit="game"):
        team_home = teams.get('home')
        team_away = teams.get('away')
        home_wins = 0
        away_wins = 0

        # Make sure both teams have players 
        # If either team is missing players, skip the simulation
        if not team_home or not team_away:
            continue
        
        # Get the team names
        home_name = team_home[0]['team']
        away_name = team_away[0]['team']

        # Initialize number of wins and ties for each team
        home_wins = away_wins = ties = 0

        # Have total scores for each team
        home_total_score = away_total_score = 0

        for _ in range(num_simulations):
            home_score, away_score = simulate_game(team_home, team_away)
            home_total_score += home_score
            away_total_score += away_score

            if home_score > away_score:
                home_wins += 1
            elif away_score > home_score:
                away_wins += 1
            else:
                ties += 1
    
        results.append({
            "game_id": game_id,
            "away_team": away_name,
            "home_team": home_name,
            "away_win_pct": away_wins / num_simulations,
            "home_win_pct": home_wins / num_simulations,
            "avg_away_score": away_total_score / num_simulations,
            "avg_home_score": home_total_score / num_simulations,
        })

    results_df = pd.DataFrame(results)
    results_df.sort_values(by="game_id", inplace=True)

    return results_df
        