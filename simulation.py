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
from collections import Counter

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
            p['single_rate'] = p['single'] / ab if p['single']/ ab > 0 else 0.12
            p['double_rate'] = p['double'] / ab if p['double']/ ab > 0 else 0.045
            p['triple_rate'] = p['triple'] / ab if p['triple']/ ab > 0 else 0.005
            p['home_run_rate'] = p['home_run'] / ab if p['home_run']/ ab > 0 else 0.1
            p['speed_rating'] = p['sprint_speed'] if p['sprint_speed'] > 0 else 25
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
    # Quick test: simulate 1000 at-bats and count outcomes


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

            # Get base runners speed rating for each base
            first_base_speed_rating = bases[0]['speed_rating'] if bases[0] is not None else None
            second_base_speed_rating = bases[1]['speed_rating'] if bases[1] is not None else None
            third_base_speed_rating = bases[2]['speed_rating'] if bases[2] is not None else None

            # Simulate the at-bat using the prior function
            result = simulate_at_bat(batter)
            
            # Sacrifice fly
            if result == "out" and bases[2] is not None and outs < 2 and base_run < third_base_speed_rating:
                runs += 1
                bases[2] = None
                outs += 1
            # Batter gets out (non sac fly opportunity)
            elif result == "out":
                outs += 1
            # Batter hits a single
            elif result == "single":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None and third_base_speed_rating is not None:
                    # Runner on third base scores
                    runs += 1
                # Runner on second base scenarios
                if bases[1] is not None and second_base_speed_rating is not None:
                    # Runner on second base scores
                    if base_run < 1 * second_base_speed_rating:
                        runs += 1
                    else:
                    # Runner on second base moves to third base
                        bases[2] = bases[1]

                # Runner on first base scenarios
                if bases[0] is not None and first_base_speed_rating is not None:
                    # Runner on first base scores
                    if (first_base_speed_rating is not None and second_base_speed_rating is None or base_run < 1 * second_base_speed_rating and
                        base_run < 0.1 * first_base_speed_rating):
                        runs += 1
                    # Runner on first base moves to third base
                    elif base_run < .5 * first_base_speed_rating and bases[2] is None:
                        # Runner on first base moves to second base
                        bases[2] = bases[0]
                    # Runner on first base moves to second base
                    else:
                    # Runner on first base moves to second base
                        bases[1] = bases[0]
                # Batter moves to first base
                bases[0] = batter
            # Batter hits a double
            elif result == "double":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None:
                    runs += 1
                # Runner on second base scenario 
                if bases[1] is not None:
                    runs += 1
                # Runner on first base scenario
                if bases[0] is not None and first_base_speed_rating is not None:
                    # Runner on first base scores
                    if base_run < .9 * first_base_speed_rating:
                        runs += 1
                    # Runner on first base moves to third base
                    else:
                        bases[2] = bases[0]
                bases[1] = batter
                bases[0] = None     
            # Batter hits a triple
            elif result == "triple":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None:
                    runs += 1
                # Runner on second base scenario
                if bases[1] is not None:
                    runs += 1
                # Runner on first base scenario
                if bases[0] is not None:
                    runs += 1
                # Batter moves to third base
                bases[2] = batter
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
        return runs, idx
    
    # Function to simulate an extra inning
    # This function is called when the game is tied after 9 innings
    def simulate_extra_inning(lineup, idx):
        previous_batter = lineup[(idx - 1) % len(lineup)]
        outs = 0
        bases = [None, previous_batter, None]
        runs = 0

        while outs < 3:
            batter = lineup[idx % len(lineup)]
            # Get a random number for runner's likelihood of running additional bases
            base_run = random.randint(0,100)

            # Get base runners speed rating for each base
            first_base_speed_rating = bases[0]['speed_rating'] if bases[0] is not None else None
            second_base_speed_rating = bases[1]['speed_rating'] if bases[1] is not None else None
            third_base_speed_rating = bases[2]['speed_rating'] if bases[2] is not None else None

            # Simulate the at-bat using the prior function
            result = simulate_at_bat(batter)

            # Sacrifice fly
            if result == "out" and bases[2] is not None and outs < 2 and base_run < third_base_speed_rating:
                runs += 1
                bases[2] = None
                outs += 1
            # Batter gets out (non sac fly opportunity)
            elif result == "out":
                outs += 1
            # Batter hits a single
            elif result == "single":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None and third_base_speed_rating is not None:
                    # Runner on third base scores
                    runs += 1
                # Runner on second base scenarios
                if bases[1] is not None and second_base_speed_rating is not None:
                    # Runner on second base scores
                    if base_run < 1 * second_base_speed_rating:
                        runs += 1
                    else:
                    # Runner on second base moves to third base
                        bases[2] = bases[1]

                # Runner on first base scenarios
                if bases[0] is not None and first_base_speed_rating is not None:
                    # Runner on first base scores
                    if (first_base_speed_rating is not None and second_base_speed_rating is None or base_run < 1 * second_base_speed_rating and
                        base_run < 0.1 * first_base_speed_rating):
                        runs += 1
                    # Runner on first base moves to third base
                    elif base_run < .5 * first_base_speed_rating and bases[2] is None:
                        # Runner on first base moves to second base
                        bases[2] = bases[0]
                    # Runner on first base moves to second base
                    else:
                    # Runner on first base moves to second base
                        bases[1] = bases[0]
                # Batter moves to first base
                bases[0] = batter
            # Batter hits a double
            elif result == "double":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None:
                    runs += 1
                # Runner on second base scenario 
                if bases[1] is not None:
                    runs += 1
                # Runner on first base scenario
                if bases[0] is not None and first_base_speed_rating is not None:
                    # Runner on first base scores
                    if base_run < .9 * first_base_speed_rating:
                        runs += 1
                    # Runner on first base moves to third base
                    else:
                        bases[2] = bases[0]
                bases[1] = batter
                bases[0] = None     
            # Batter hits a triple
            elif result == "triple":
                # Simulates runners
                # Runner on third base scenario
                if bases[2] is not None:
                    runs += 1
                # Runner on second base scenario
                if bases[1] is not None:
                    runs += 1
                # Runner on first base scenario
                if bases[0] is not None:
                    runs += 1
                # Batter moves to third base
                bases[2] = batter
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
        return runs, idx 

    # Function to simulate a game
    def simulate_game(team_home, team_away):
        # Initialize the scores and indices for both teams
        home_score = away_score = 0
        home_idx = away_idx = 0
        total_innings = 0

        # Simulate 9 innings of play
        for inning in range(9):
            # Simulate the away half of the inning
            away_runs, away_idx = simulate_half_inning(team_away, away_idx)
            away_score += away_runs
            # Simulate the home half of the inning
            home_runs, home_idx = simulate_half_inning(team_home, home_idx)
            home_score += home_runs
            # Add to the total innings played
            total_innings += 1
        
        # If the game is tied after 9 innings, go to extra innings
        if home_score == away_score:
            inning = 9
            while home_score == away_score:
                # Simulate the away half of the inning
                away_runs, away_idx = simulate_extra_inning(team_away, away_idx)
                away_score += away_runs
                # Simulate the home half of the inning
                home_runs, home_idx = simulate_extra_inning(team_home, home_idx)
                home_score += home_runs
                inning += 1
                # Add to the total innings played
                total_innings += 1
        
        return home_score, away_score, total_innings
    
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
        total_innings_sum = 0

        for _ in range(num_simulations):
            home_score, away_score, total_innings = simulate_game(team_home, team_away)
            home_total_score += home_score
            away_total_score += away_score
            total_innings_sum += total_innings
            if home_score > away_score:
                home_wins += 1
            else:
                away_wins += 1
    
        results.append({
            "Game ID": game_id,
            "Projected Winning Team": home_name if home_wins > away_wins else away_name,
            "Projected Losing Team": away_name if home_wins > away_wins else home_name,
            "Away Team": away_name,
            "Home Team": home_name,
            "Away Team Win Percentage": away_wins / num_simulations,
            "Home Team Win Percentage": home_wins / num_simulations,
            "Average Away Score": away_total_score / num_simulations,
            "Average Home Score": home_total_score / num_simulations,
            "Average Total Innings": total_innings_sum / num_simulations,
            "Confidence Level": home_wins / num_simulations if home_wins > away_wins else away_wins / num_simulations
        })
    

    results_df = pd.DataFrame(results)
    results_df.sort_values(by="Confidence Level", ascending= False, inplace=True)

    return results_df

    