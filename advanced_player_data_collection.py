from pybaseball import statcast_batter
import pandas as pd

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

# Calculate the player's batting average against right-handed pitchers (RHP) and left-handed pitchers (LHP)
batting_avg_rhp = vs_rhp['events'].value_counts().get('hit', 0) / len(vs_rhp) if len(vs_rhp) > 0 else 0
batting_avg_lhp = vs_lhp['events'].value_counts().get('hit', 0) / len(vs_lhp) if len(vs_lhp) > 0 else 0

# Print the results
print(f"Aaron Judge's Batting Average vs RHP: {batting_avg_rhp:.3f}")
print(f"Aaron Judge's Batting Average vs LHP: {batting_avg_lhp:.3f}")