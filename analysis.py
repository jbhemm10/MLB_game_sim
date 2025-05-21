"""
This script runs an analysis on the simulated games and actual games.
INPUTS:
- Simulated game data
- Actual game data
OUTPUTS:
- CSV files containing the analysis results
"""

# Import the necessary libraries
import pandas as pd
import os
from datetime import datetime, timedelta
import requests

# Set todays date
date = datetime.now()
yesterday = (date - timedelta(days=1)).strftime("%Y-%m-%d")

# Function to collect the actual game data from the day before using the MLB API
def get_yesterdays_scores():
    
    # MLB API endpoint for schedule and scores
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={yesterday}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from MLB API.")

    data = response.json()
    if not data.get("dates"):
        print(f"No games were scheduled on {yesterday}.")
        return

    game_results = []
    for game in data["dates"][0]["games"]:
        if game["status"]["detailedState"] == "Final":
            game_results.append({
                "game_id": game["gamePk"],
                "date": yesterday,
                "away_team": game["teams"]["away"]["team"]["name"],
                "away_score": game["teams"]["away"]["score"],
                "home_team": game["teams"]["home"]["team"]["name"],
                "home_score": game["teams"]["home"]["score"],
                "winner": (
                    game["teams"]["home"]["team"]["name"]
                    if game["teams"]["home"]["score"] > game["teams"]["away"]["score"]
                    else game["teams"]["away"]["team"]["name"]
                )
            })
    
    # Save the results to a CSV file
    actual_results = pd.DataFrame(game_results)

    # Check if the directory exists, if not create it
    if not os.path.exists("actual_outcomes"):
        os.makedirs("actual_outcomes")
    
    # Save the DataFrame to a CSV file
    actual_results.to_csv(f"actual_outcomes/actual_results_{yesterday}.csv", index=False)

def simulation_analysis():
    # Load the simulated game data
    simulated_data = pd.read_csv(f"simulated_games/simulated_games_{yesterday}.csv")

    # Load the actual game data
    actual_data = pd.read_csv(f"actual_outcomes/actual_results_{yesterday}.csv")

    # Pull game IDs from the simulated data
    simulated_game_ids = simulated_data["Game ID"].unique()

    # Pull game IDs from the actual data
    actual_game_ids = actual_data["game_id"].unique()

    # Load existing analysis to check for duplicates
    existing_analysis = pd.read_csv("simulation_analysis.csv") if os.path.exists("simulation_analysis.csv") else pd.DataFrame()

    # Run through each simulated and actual game to see if the winners match
    results = []
    for game_id in simulated_game_ids:
        if game_id in actual_game_ids:
            # Skip if the game has already been processed
            if not existing_analysis.empty and (
                (existing_analysis["Game ID"] == game_id) & (existing_analysis["Date"] == yesterday)
            ).any():
                continue
            # Get the simulated and actual winners
            simulated_winner = simulated_data[simulated_data["Game ID"] == game_id]["Projected Winning Team"].values[0]
            actual_winner = actual_data[actual_data["game_id"] == game_id]["winner"].values[0]
            # Get home and away teams
            home_team = simulated_data[simulated_data["Game ID"] == game_id]["Home Team"].values[0]
            away_team = simulated_data[simulated_data["Game ID"] == game_id]["Away Team"].values[0]
            # Get confidence level
            if simulated_winner == home_team:
                confidence = simulated_data[simulated_data["Game ID"] == game_id]["Home Team Win Percentage"].values[0]
            else:
                confidence = simulated_data[simulated_data["Game ID"] == game_id]["Away Team Win Percentage"].values[0]
            # Store the results
            results.append({
                "Game ID": game_id,
                "Date": yesterday,
                "Matchup": f"{simulated_data[simulated_data['Game ID'] == game_id]['Away Team'].values[0]} vs {simulated_data[simulated_data['Game ID'] == game_id]['Home Team'].values[0]}",
                "Simulated Winner": simulated_winner,
                "Actual Winner": actual_winner,
                "Correctly Predicted": 1 if simulated_winner == actual_winner else 0,
                "Confidence": confidence
            })
    
    # Save the results to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv("simulation_analysis.csv", mode='a', header=not os.path.exists("simulation_analysis.csv"), index=False)

    # Calculate and print overall accuracy
    if os.path.exists("simulation_analysis.csv"):
        full_df = pd.read_csv("simulation_analysis.csv")
        overall_accuracy = full_df["Correctly Predicted"].mean()
        print(f"Overall accuracy: {overall_accuracy:.2%}")
    else:
        print("No historical accuracy data available yet.")
    
    # Calculate and print yesterday's accuracy
    if "Correctly Predicted" in results_df.columns:
        yesterday_accuracy = results_df["Correctly Predicted"].mean()
        print(f"Yesterday's accuracy: {yesterday_accuracy:.2%}")
    else:
        yesterday_accuracy = full_df[full_df["Date"] == yesterday]["Correctly Predicted"].mean()
        print(f"Yesterday's accuracy: {yesterday_accuracy:.2%}")

    # Calculate the overall confidence for each correctly predicted game
    overall_confidence = full_df[full_df["Correctly Predicted"] == 1]["Confidence"].mean() if not full_df[full_df["Correctly Predicted"] == 1].empty else 0
    print(f"Overall confidence for correctly predicted games: {overall_confidence:.3%}")
    # Calculate the min and max confidence for each correctly predicted game
    min_confidence = full_df[full_df["Correctly Predicted"] == 1]["Confidence"].min() if not full_df[full_df["Correctly Predicted"] == 1].empty else 0
    max_confidence = full_df[full_df["Correctly Predicted"] == 1]["Confidence"].max() if not full_df[full_df["Correctly Predicted"] == 1].empty else 0
    print(f"Min confidence for correctly predicted games: {min_confidence:.3%}")
    print(f"Max confidence for correctly predicted games: {max_confidence:.3%}")