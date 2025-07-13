from pybaseball import statcast_batter
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from lineups_collection import get_lineups_for_date
from typing import List

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

def get_player_splits(player_ids: List[int], start_date: str, end_date: str):

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
            print(f"Error retrieving data for player {player_id}: {e}")

    # Only concatenate if we have data
    if all_player_data:
        all_data_df = pd.concat(all_player_data.values(), keys=all_player_data.keys(), names=['player_id', 'index'])
        all_data_df.reset_index(level=0, inplace=True)
        all_data_df.to_csv('2025_advanced_hitter_data.csv', index=False)
        print(f"Saved {len(all_player_data)} players' data to 2025_advanced_hitter_data.csv")
    else:
        print("No data collected for any player.")

    # Pull player names from the data frame
    player_names = all_data_df.groupby('player_id')['player_name'].first().reset_index()


    # Find number of plate appearances, at bats, hits, singles, doubles, triples, home runs, walks and strikeouts against right-handed pitchers
    pa_vs_rhp = all_data_df[all_data_df['p_throws'] == 'R'].groupby('player_id').size().reset_index(name='plate_appearances')
    at_bats_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & all_data_df['events'].isin(['single', 'double', 'triple', 'home_run', 'strikeout', 'field_out', 'force_out', 'grounded_into_double_play'])].groupby('player_id').size().reset_index(name='at_bats')
    hits_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & all_data_df['events'].isin(['single', 'double', 'triple', 'home_run'])].groupby('player_id').size().reset_index(name='hits')
    walks_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & all_data_df['events'].isin(['walk', 'hit_by_pitch', 'intentional_walk'])].groupby('player_id').size().reset_index(name='walks')
    strikeouts_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & all_data_df['events'].isin(['strikeout'])].groupby('player_id').size().reset_index(name='strikeouts')
    singles_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & (all_data_df['events'] == 'single')].groupby('player_id').size().reset_index(name='singles')
    doubles_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & (all_data_df['events'] == 'double')].groupby('player_id').size().reset_index(name='doubles')
    triples_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & (all_data_df['events'] == 'triple')].groupby('player_id').size().reset_index(name='triples')
    home_runs_vs_rhp = all_data_df[(all_data_df['p_throws'] == 'R') & (all_data_df['events'] == 'home_run')].groupby('player_id').size().reset_index(name='home_runs')

    # Merge all right-handed pitcher statistics into a single DataFrame
    stats_vs_rhp_df = player_names.merge(pa_vs_rhp, on='player_id', how='outer') \
        .merge(at_bats_vs_rhp, on='player_id', how='outer') \
        .merge(hits_vs_rhp, on='player_id', how='outer') \
        .merge(singles_vs_rhp, on='player_id', how='outer') \
        .merge(doubles_vs_rhp, on='player_id', how='outer') \
        .merge(triples_vs_rhp, on='player_id', how='outer') \
        .merge(home_runs_vs_rhp, on='player_id', how='outer') \
        .merge(walks_vs_rhp, on='player_id', how='outer') \
        .merge(strikeouts_vs_rhp, on='player_id', how='outer') \

    # Find number of plate appearances, at bats, hits, singles, doubles, triples, home runs, walks and strikeouts against left-handed pitchers
    pa_vs_lhp = all_data_df[all_data_df['p_throws'] == 'L'].groupby('player_id').size().reset_index(name='plate_appearances')
    at_bats_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & all_data_df['events'].isin(['single', 'double', 'triple', 'home_run', 'strikeout', 'field_out', 'force_out', 'grounded_into_double_play'])].groupby('player_id').size().reset_index(name='at_bats')
    hits_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & all_data_df['events'].isin(['single', 'double', 'triple', 'home_run'])].groupby('player_id').size().reset_index(name='hits')
    walks_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & all_data_df['events'].isin(['walk', 'hit_by_pitch', 'intentional_walk'])].groupby('player_id').size().reset_index(name='walks')
    strikeouts_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & all_data_df['events'].isin(['strikeout'])].groupby('player_id').size().reset_index(name='strikeouts')
    singles_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & (all_data_df['events'] == 'single')].groupby('player_id').size().reset_index(name='singles')
    doubles_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & (all_data_df['events'] == 'double')].groupby('player_id').size().reset_index(name='doubles')
    triples_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & (all_data_df['events'] == 'triple')].groupby('player_id').size().reset_index(name='triples')
    home_runs_vs_lhp = all_data_df[(all_data_df['p_throws'] == 'L') & (all_data_df['events'] == 'home_run')].groupby('player_id').size().reset_index(name='home_runs')

    # Merge all left-handed pitcher statistics into a single DataFrame
    stats_vs_lhp_df = player_names.merge(pa_vs_lhp, on='player_id', how='outer') \
        .merge(at_bats_vs_lhp, on='player_id', how='outer') \
        .merge(hits_vs_lhp, on='player_id', how='outer') \
        .merge(singles_vs_lhp, on='player_id', how='outer') \
        .merge(doubles_vs_lhp, on='player_id', how='outer') \
        .merge(triples_vs_lhp, on='player_id', how='outer') \
        .merge(home_runs_vs_lhp, on='player_id', how='outer') \
        .merge(walks_vs_lhp, on='player_id', how='outer') \
        .merge(strikeouts_vs_lhp, on='player_id', how='outer')

    # Create a label for the handedness of the pitcher
    rhp_df = all_data_df[all_data_df['p_throws'] == 'R'].copy()
    rhp_df['Pitcher Handedness'] = 'R'

    lhp_df = all_data_df[all_data_df['p_throws'] == 'L'].copy()
    lhp_df['Pitcher Handedness'] = 'L'

    # Combine the two DataFrames
    split_df = pd.concat([rhp_df, lhp_df], ignore_index=True)

    # Step 3: Add derived columns for grouping
    split_df['is_ab'] = split_df['events'].isin([
        'single', 'double', 'triple', 'home_run', 'strikeout',
        'field_out', 'force_out', 'grounded_into_double_play', 'other_out'
    ])
    split_df['is_hit'] = split_df['events'].isin(['single', 'double', 'triple', 'home_run'])
    split_df['is_single'] = split_df['events'] == 'single'
    split_df['is_double'] = split_df['events'] == 'double'
    split_df['is_triple'] = split_df['events'] == 'triple'
    split_df['is_home_run'] = split_df['events'] == 'home_run'
    split_df['is_plate_appearance'] = split_df['events'].notna() & (split_df['events'] != '')
    split_df['is_walks'] = split_df['events'].isin(['walk', 'hit_by_pitch', 'intentional_walk'])
    split_df['is_strikeouts'] = split_df['events'] == 'strikeout'

    # Step 4: Group by player + pitcher handedness
    split_stats = split_df.groupby(['player_id', 'Pitcher Handedness']).agg({
        'is_ab': 'sum',
        'is_hit': 'sum',
        'is_single': 'sum',
        'is_double': 'sum',
        'is_triple': 'sum',
        'is_home_run': 'sum',
        'is_plate_appearance': 'size',
        'is_walks': 'sum',
        'is_strikeouts': 'sum'
    }).rename(columns={
        'is_ab': 'ab',
        'is_hit': 'hit',
        'is_single': 'single',
        'is_double': 'double',
        'is_triple': 'triple',
        'is_home_run': 'home_run',
        'is_plate_appearance': 'pa',
        'is_walks': 'walk',
        'is_strikeouts': 'strikeout'
    }).reset_index()

    # Replace NaN values with 0
    split_stats.fillna(0, inplace=True)

    # Step 5: Calculate stats
    split_stats['batting_avg'] = split_stats['hit'] / split_stats['ab'].replace(0, pd.NA)
    split_stats['slg_percent'] = (
        split_stats['single'] + 2 * split_stats['double'] +
        3 * split_stats['triple'] + 4 * split_stats['home_run']
    ) / split_stats['ab'].replace(0, pd.NA)

    # Merge names into the split stats
    split_stats = split_stats.merge(player_names, on='player_id', how='left')

    # Optional: Rearrange columns so the name comes first
    split_stats = split_stats[[
        'player_id', 'player_name', 'Pitcher Handedness', 'pa',
        'ab', 'hit', 'single', 'double', 'triple', 'home_run', 'walk', 'strikeout',
        'batting_avg', 'slg_percent'
    ]]

    # Data file name
    file_name = f'2025_hitter_split_stats.csv'

    # Save the split statistics DataFrame to a CSV file
    split_stats.to_csv(file_name, index=False)
    print(f"Saved split statistics to {file_name}")

    return split_stats