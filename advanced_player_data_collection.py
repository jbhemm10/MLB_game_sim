from pybaseball import statcast_batter
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from lineups_collection import get_lineups_for_date

# Set today's date
today = datetime.now().strftime('%Y-%m-%d')
season_start = '2025-03-27'

# Get lineups
lineups = get_lineups_for_date(today, save_to_file=False)

# Collect unique player IDs from today's lineups
player_ids = set()
for lineup in lineups:
    for player in lineup['home_lineup']:
        player_ids.add(player['player_id'])
    for player in lineup['away_lineup']:
        player_ids.add(player['player_id'])

# Convert player IDs to a list
player_ids = list(player_ids)
total_players = len(player_ids)

# Function to get player at-bat data
def get_player_at_bats(player_id):
    df = statcast_batter(season_start, today, player_id)

    # Filter only rows with meaningful 'events' (i.e., actual plate appearances)
    df = df[df['events'].notna() & (df['events'] != '')]

    # Sort by game and appearance order
    df = df.sort_values(by=['game_date', 'n_priorpa_thisgame_player_at_bat'], ascending=[False, False])
    
    columns_to_keep = ['player_id', 'player_name', 'game_date', 'n_priorpa_thisgame_player_at_bat', 'events', 'batter', 'pitcher', 
                       'p_throws', 'on_3b', 'on_2b', 'on_1b', 'stand']
    
    df =df[[col for col in columns_to_keep if col in df.columns]]
    return df

# Get all valid player data
all_player_data = {}

for player_id in tqdm(player_ids, desc="Retrieving player data", unit="player", total=total_players):
    try:
        df = get_player_at_bats(player_id)
        if not df.empty:
            all_player_data[player_id] = df
        else:
            print(f"Player ID {player_id}: No valid data.")
    except Exception as e:
        print(f"Error retrieving data for player ID {player_id}: {e}")

# Only concatenate if we have data
if all_player_data:
    all_data_df = pd.concat(all_player_data.values(), keys=all_player_data.keys(), names=['player_id', 'index'])
    all_data_df.reset_index(level=0, inplace=True)
    all_data_df.to_csv('2025_advanced_hitter_data.csv', index=False)
    print(f"Saved {len(all_player_data)} players' data to 2025_advanced_hitter_data.csv")
else:
    print("No data collected for any player.")


"""
# Get at bat data for for a specific player (Aaron Judge)
df = statcast_batter('2025-03-27', '2025-11-01', '592450')

# Remove rows where 'events' is empty or NaN
df = df[df['events'].notna() & (df['events'] != '')]

# Order the dataframe by 'game_date' descending and 'n_priorpa_thisgame_player_at_bat'
df = df.sort_values(by=['game_date', 'n_priorpa_thisgame_player_at_bat'], ascending=[False, False])

# Save data to a CSV file
df.to_csv('aaron_judge_at_bats_2025.csv', index=False)

vs_rhp = df[df['p_throws'] == 'R']
vs_lhp = df[df['p_throws'] == 'L']

# Create classifies for hits, outs, and at bats
hit_results = ['single', 'double', 'triple', 'home_run']
out_results = ['out', 'strikeout', 'field_out', 'force_out', 'grounded_into_double_play']
walk_results = ['walk', 'hit_by_pitch', 'intentional_walk']

# Find number of walks
num_walks = df['events'].apply(lambda x: 1 if x in walk_results else 0).sum()

# Print the number of walks
print(f"Number of walks: {num_walks}")

# Find number of hits
num_hits = df['events'].apply(lambda x: 1 if x in hit_results else 0).sum()

# Print the number of hits
print(f"Number of hits: {num_hits}")

# Find number of plate appearances
num_plate_appearances = df['events'].notna().sum()

# Print the number of plate appearances
print(f"Number of plate appearances: {num_plate_appearances}")

# Calculate batting average splits
batting_avg_rhp = vs_rhp

# Calculate batting averages against right-handed pitchers (RHP) and left-handed pitchers (LHP)
batting_avg_rhp = vs_rhp['events'].apply(lambda x: 1 if x in hit_results else 0).sum() / (vs_rhp['events'].apply(lambda x: 1 if x in hit_results + out_results else 0).sum() or 1)
batting_avg_lhp = vs_lhp['events'].apply(lambda x: 1 if x in hit_results else 0).sum() / (vs_lhp['events'].apply(lambda x: 1 if x in hit_results + out_results else 0).sum() or 1)

# Print the results
print(f"Aaron Judge's Batting Average vs RHP: {batting_avg_rhp:.3f}")
print(f"Aaron Judge's Batting Average vs LHP: {batting_avg_lhp:.3f}")

# Calculate on base percentage (OBP)
obp = (num_hits + num_walks) / (num_plate_appearances or 1)

# Print OBP
print(f"Aaron Judge's On Base Percentage: {obp:.3f}")
"""