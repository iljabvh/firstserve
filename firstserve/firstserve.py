from copy import deepcopy
from pathlib import Path
from .utils_extract_data import (open_cfg_asdict, check_playerkey, add_new_player_to_db,
                                 add_empty_match_to_db, incr_one_match_to_db, calc_stat_update, set_matchwinner, decide_setsplayed)
from math import isnan


"""
Main class(es) in this package are stored here.
PlayersDB: Setting up a players dictionary database, including matches and statistics for players
"""


class PlayersDB:
    def __init__(self, config_path):
        """
        Initialize configurations to handle the CSV data.
        The methods are adjusted to extract data from the datasets here:
         https://www.kaggle.com/datasets/hwaitt/tennis-20112019 (atp.csv and wta.csv)
        """

        assert isinstance(config_path, (str, Path))
        self.config = open_cfg_asdict(config_path)
        self.stats_dict = self.config['players_settings']['stats_dict']
        self.match_formats = self.config['dataset_config']['generate']['ImportMatchFormats']

    def generate_players_template(self):
        """
        Generates a template to include player statistics like winrate, first serve pct., break ball conversion, etc.
        """
        players_dict = {'Players': {}}

        players_template = self.config['players_settings']['players_stats']
        players_dict['template'] = deepcopy(players_template)

        return players_dict

    def add_match_stats_to_db(self, players_dict, player, matches_dict, matchidx):
        """
        players_dict: dictionary of all player stats
        player: player
        matches_dict: match_dictionary. We need this to check if the match value in the csv is valid or NaN.
        stats_dict: translates the naming from the csv into my chosen naming, e.g., 'Serve1stPCT_': 'FirstServePCT'.
        The function check_playerkey takes ['1', '2'] to see whether we include the stat into 'FirstServePCT'
         taken from 'Serve1stPCT_1' for 'Name_1' or from 'Serve1stPCT_2' for 'Name_2'
        """

        players_template = players_dict['template']

        for statkey in self.stats_dict.keys():
            """
            statkey is e.g. 'Serve1stPCT_' or 'ReceivingPointsWonPCT_', etc.
            """
            if self.stats_dict[statkey] in players_template:
                """
                playerkey is either 'Name_1' or 'Name_2'. We want to know whether we update stats for player known under 'Name_1' or under 'Name_2'
                """
                playerkey = check_playerkey(player, statkey, matches_dict, matchidx)

                if isnan(matches_dict[playerkey][matchidx]):
                    """
                    No value in the dataset, so we do not update this stat for this player. 
                    This means there was no entry for first serve won percentage or some other stat
                    """
                    continue
                else:
                    """
                    We update the value self.stats_dict[statkey] and store it in players_dict
                    """
                    player_stat_to_update = players_dict['Players'][player][self.stats_dict[statkey]]
                    match_stat_for_update = matches_dict[playerkey][matchidx]
                    calc_stat_update(player_stat_to_update, match_stat_for_update)

        return None

    def add_stats_to_match_db(self, players_dict, matchstat_dict, player, matches_dict, matchidx):

        players_template = players_dict['template']

        for statkey in self.stats_dict.keys():
            if self.stats_dict[statkey] in players_template:
                playerkey = check_playerkey(player, statkey, matches_dict, matchidx)
                if isnan(matches_dict[playerkey][matchidx]):
                    """
                    No value in the dataset, so we do not update this stat for this player. 
                    This means there was no entry for first serve won percentage or some other stat
                    """
                    continue
                else:
                    """
                    We update the value self.stats_dict[statkey] it in matchstat_dict to have information about the current match
                    after it is finished (hence 'postmatch')
                    """
                    matchstat_dict[matchidx]['postmatch'][player][self.stats_dict[statkey]] = matches_dict[playerkey][matchidx]

        return None

    def add_stats_from_rel_outcomes(self, players_dict, matches_dict):
        """
        param: players_dict: dictionary with Player stats
        param: matchid_list: list of match indeces indexed for an iteration over matches_dict
        param: matches_dict: dictionary of matches, indlucing results relative to both players. I.e. 6-4 6-2 for one player, and 2-6 4-6 for the other player.
        The code is adjusted to use the data set from https://www.kaggle.com/datasets/hwaitt/tennis-20112019 (atp.csv and wta.csv).
        As you see, unfortunately the results are mirrored and the correct result is the winning outcome, 6-4 6-2 in this case.
        It is a bit tedious to check which player has won because of the mirrored scorelines, but this method is doing exactly that.
        return updated Players database dictionary after including the matches from matches_dict
        """

        """ Check the format of the match"""
        assert ('Bo3' or 'Bo5') in self.match_formats, "No match formats in list - no matches can be added!"

        players_dict = deepcopy(players_dict)
        matchstat_dict = {}

        """
        The reason the code below is so complicated is because of the mirrored scorelines. 
        So we have to perform multiple checks to ensure we have the correct scoreline with the correct winner. Note that we always have two scorelines:
        One relative to player 'Name_1' and one relative to 'Name_2' with one scoreline being mirrored and wrong. The correct scoreline is either 'Result_CUR_1'
        or 'Result_CUR_2'.
        """

        match_index_list = list(matches_dict['ID'])

        for matchidx in match_index_list:

            if matchidx % 10000 == 0:
                print('Importing match : ', matchidx)

            """
            For each match (entry), we split every set and count the number of sets below:
            if len(rel_match_result) == 2 for each split string, it's a two-set match
            """

            match_results = [matches_dict['Result_CUR_1'][matchidx].split(), matches_dict['Result_CUR_2'][matchidx].split()]
            player1_str, player2_str = [matches_dict['Name_1'][matchidx], matches_dict['Name_2'][matchidx]]

            if (all(len(rel_match_result) == 2 for rel_match_result in match_results) or
                    all(len(rel_match_result) == 3 for rel_match_result in match_results)):
                """
                Two sets played or three sets played.
                twosetsplayed/threesetsplayed is a dictionary in style {player1: setswon_by_player1, player2: setswon_by_player2}, 
                showing both players as keys with int number of sets won by each as item. 
                We need to use this method twice because we have two relative match results: 'Result_CUR_1' and 'Result_CUR_2'. 
                We have two dictionaries in twosetsplayed_rel to compare whether the data consistently shows the correct winner for both relative scorelines.
                """
                matchstat_dict[matchidx] = add_empty_match_to_db(player1_str, player2_str)
                allsetsplayed_rel = decide_setsplayed(match_results, player1_str, player2_str)

            else:
                """Bo5 format is not implemented yet and the dataset does probably not display correct Bo5 match outcomes."""
                continue

            """
            Check both setwinners_dict_rel entries to see whether results are consistent and retrieve 'winner' and 'loser'.
            """
            winner, loser = set_matchwinner(allsetsplayed_rel, player1_str, player2_str)

            """
            Update the entries in players_dict for both players, winner and loser with incr_one_match_to_db. 
            If a player is missing, make a new entry with add_new_player_to_db.
            """

            for player in [winner, loser]:
                if player not in players_dict['Players']:
                    add_new_player_to_db(players_dict, player)
                matchstat_dict[matchidx]['prematch'][player] = deepcopy(players_dict['Players'][player])

            incr_one_match_to_db(players_dict, loser, {'won': False})
            incr_one_match_to_db(players_dict, winner, {'won': True})

            for player in [winner, loser]:
                self.add_match_stats_to_db(players_dict, player, matches_dict, matchidx)
                self.add_stats_to_match_db(players_dict, matchstat_dict, player, matches_dict, matchidx)

            matchstat_dict[matchidx]['winner'] = winner

            """
            Here we store the matches with all the necessary stats
            """

        return players_dict, matchstat_dict
