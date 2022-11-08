from firstserve.firstserve import PlayersDB
from firstserve.utils_extract_data import import_csv, open_cfg_asdict
import matplotlib.pyplot as plt

file_location = f'./tennisdata/wta.csv'  # you can also use wta.csv, both taken from https://www.kaggle.com/datasets/hwaitt/tennis-20112019
tennisdata = import_csv(file_location)

"""
read/open config file where we find information on how to initialize 'Players'
"""

cfg_path = f"./configs/config_simpledb.yml"
config_test = open_cfg_asdict(cfg_path)

print('### Finished loading data set ###')

NewPlayersClass = PlayersDB(cfg_path)
players_new_dict = NewPlayersClass.generate_players_template()

print('### Starting to extract player / match statistics from loaded data set ###')

players_dict, matches_dict = NewPlayersClass.add_stats_from_rel_outcomes(players_new_dict, tennisdata)

print('### Demonstrating extracted data: ###')

"""
Plotting winrates and firstserve percentages
Only consider data which is made up from more than match_number_filter matches
"""

match_number_filter = 500
perf_metric = 'WinrateTotal'
players_performance = []
players_names = []
xr = []

for key in players_dict['Players'].keys():
    # perf, perf_metric_matches = players_dict['Players'][key][perf_metric]
    perf, perf_metric_matches = players_dict['Players'][key][perf_metric], players_dict['Players'][key]['Number of Matches']

    if perf == 0.:
        """
        No data available
        """
        continue
    elif perf_metric_matches < match_number_filter:
        """
        Too few matches played to trust performance metric
        """
        continue

    players_performance.append(perf)
    players_names.append(key)

xr = range(len(players_performance))
"""
Annotate players
"""
fig, ax = plt.subplots()
for i, txt in enumerate(players_names):
    ax.annotate(txt, (xr[i], players_performance[i]))
ax.scatter(xr, players_performance)
plt.show()

print('### Finished demo script (feel free to play around in this script!) ###')
