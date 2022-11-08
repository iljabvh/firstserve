from copy import deepcopy
import yaml
from pandas import read_csv
import sys


def incr_one_match_to_db(players_dict, player, outcome):
    """
    :param players_dict: Players dictionary, as initialized in the above function
    :param player: Player string
    :param outcome: won, lost. Other stats (retired, disqualified) will be implemented later

    In this function we simply account for a match that was played by player.
    No of Matches increases and his winrate is changed, depending on :param outcome:.
    """

    players_template = players_dict['template']

    if 'Number of Matches' in players_template:
        players_dict['Players'][player]['Number of Matches'] += 1
    if ('WinsTotal' in players_template) and outcome['won']:
        players_dict['Players'][player]['WinsTotal'] += 1
    if 'WinrateTotal' in players_template:
        players_dict['Players'][player]['WinrateTotal'] = players_dict['Players'][player]['WinsTotal'] / \
                                                          players_dict['Players'][player]['Number of Matches']

    return None


def calc_stat_update(player_stat, match_stat_curr):
    """
    updating player_stat probability after a match, e.g. first serve percentage or returned points percentage or others
    stored in the config file in 'players_settings' -> 'stats_dict'
    """
    if player_stat[1] == 0:
        """
        If initial value of probability is 0, then set the 'matches_dict[playerkey][matchid]' probability as the new value to 
        player_stat[0]. Also increment the no. of matches player_stat[1]
        used to calculate the probability
        """
        player_stat[0] = match_stat_curr
    else:
        match_count_last = player_stat[1]
        p_curr = match_stat_curr
        p_last = player_stat[0]
        player_stat[0] = (p_curr + match_count_last * p_last) / (1 + match_count_last)

    """
    Increment the number of matches which is used to calculate the current / next probability
    """
    player_stat[1] += 1

    return None


def set_matchwinner(setsplayed_rel, player1, player2):
    """
    setsplayed_rel example: [dict(player2:2, player1:1), dict(player2:2, player1:1)]. We count the sets and decide who won the match
    """

    if (setsplayed_rel[0][player1] > setsplayed_rel[0][player2]) and (
            setsplayed_rel[1][player1] > setsplayed_rel[1][player2]):
        winner = player1
        loser = player2
    elif (setsplayed_rel[0][player2] > setsplayed_rel[0][player1]) and (
            setsplayed_rel[1][player2] > setsplayed_rel[1][player1]):
        winner = player2
        loser = player1
    else:
        sys.exit("Contradictions between results relative to player 1 and results relative to player 2")

    return winner, loser


def decide_setsplayed(match_results, player1, player2):
    """
    match_results: list of relative match results, i.e. [['6-4','6-2'], ['2-6', '4-6']]

    allsetsplayed_rel gives a list of two dictionaries:
    The dictionaries in the list show the winners relative to player1 and relative to  player2:
    Examples: [dict(player1:2, player2:0), dict(player1:2, player2:0)]
    or somtheing like [dict(player2:2, player1:1), dict(player2:2, player1:1)] if three sets were played
    """

    if all(len(rel_match_result) == 2 for rel_match_result in match_results):
        """
        Two sets were played
        """
        allsetsplayed_rel = [twosetsplayed(player1, player2, match_results[0]),
                             twosetsplayed(player2, player1, match_results[1])]
    else:
        """
        Three sets were played
        """
        allsetsplayed_rel = [threesetsplayed(player1, player2, match_results[0]),
                             threesetsplayed(player2, player1, match_results[1])]

    assert all(len(setsplayed_players) == 2 for setsplayed_players in
               allsetsplayed_rel), "There have to be two players to participate in a match."

    return allsetsplayed_rel


def twosets_check_leadingzeroes(sets_to_games):
    """
    Both sets have been split to games:
    sets_to_games: example that does not need to be corrected: [['6','4'], ['6', '2']].
    Example with the critical leading zero bug: [['4','6'], ['01', '8']]
    """
    result_list_corrected = []
    for games in sets_to_games:
        """
        Check if '0' is leading, like in the mirrored '10'. If so, then invert string to restore '10' without the leading bug.
        """
        if len(games[0]) > 1 and games[0][0] == '0':
            games[0] = games[0][::-1]
        if len(games[1]) > 1 and games[1][0] == '0':
            games[1] = games[1][::-1]

        """
        rejoin repaired string, ['01', '8'] -> ['10', '8'] -> ['10-8'] 
        """
        result_list_corrected.append('-'.join(games))

    allsets = [playedset.split('-') for playedset in result_list_corrected]

    return allsets


def threesets_check_leadingzeroes(result_list):
    """
    results_list: example that needs to be corrected: [['12-91'], ['6-3'], ['2-6']]
    In the three-set case, we only look at the leading zeroes from the first, mirrored set: ['12-91']
    If the tie-break result has two digits, then we invert the strings to account for the case: ['12-91'] -> ['21-19']
    """
    games_split = result_list[0].split('-')
    if len(games_split[0]) > 1:
        games_split[0] = games_split[0][::-1]
    if len(games_split[1]) > 1:
        games_split[1] = games_split[1][::-1]

    games_split = [games_split[0], games_split[1]]
    result_list[0] = '-'.join(games_split)
    allsets = [x.split('-') for x in result_list]

    return allsets


def count_sets(allsets, player1, player2):
    """
    allsets: [['6','4'], ['6','2']]
    counting won sets into a dictionary
    Note: player1 always has the index 0 game, player2 has the index 1 game
    """
    setcount_dict = {player1: 0, player2: 0}

    for playedset in allsets:
        gamesint = [int(gamesstr) for gamesstr in playedset]
        if gamesint[0] > gamesint[1]:
            setcount_dict[player1] += 1
        elif gamesint[1] > gamesint[0]:
            setcount_dict[player2] += 1
        else:
            sys.exit("Set result cannot have equal games by both players!")
        """
        Dictionary setcount_dict should look like dict('Player1': 2, 'Player2': 0)
        """
    return setcount_dict


def twosetsplayed(player1, player2, result_list):
    """
    :param player1: First player
    :param player2: Second player, opponent of First player
    :param result_list: results, in style ['6-4', '7-6']. A result_list argument always needs to have two items.
    :return:
    """

    assert len(result_list) == 2, "Only two sets have been played in this match"

    """
    Checking both sets for leading zeroes resulting from an annoying mirroring error from the csv data. 
    The error can happen when there is a match tie-break in the second (!!!) set, i.e. 6-2, 10-8.
    """
    sets_split_to_games = [result_entry.split('-') for result_entry in result_list]
    allsets = twosets_check_leadingzeroes(sets_split_to_games)

    """
    Finally we account for the won sets by both players and store them into a dictionary
    """

    sets_counted_dict = count_sets(allsets, player1, player2)

    return sets_counted_dict


def threesetsplayed(player1, player2, result_list):
    """
    this function counts won sets for each Player in a three-set match in the Bo3 format
    :param player1: First player
    :param player2: Second player, opponent of First player
    :param result_list: results, in style ['6-4', '2-6', '7-5'].
    :return:
    """

    """
    check for leading zeroes in score
    why? because in the data I have used the results are mirrored for some reason, and some edge cases break the function: 
    ['6-4', '2-6', '10-8'], mirrored: ['01-8', '6-2', '4-6'].
    Basically, match tiebreaks with a score 10-8 are the breaking cases, but also 20-18 and 21-19, mirrored as 81-02 and 91-12 respectively. 
    In such cases, we have to correct the '01-8' set result to count the sets correctly. The third/first set is the only problematic one. 
    In the following lines, test for this weird bug, and mirror results of the first/third set if the bug is present.
    Note that we only have to check the first set result_list[0], since there is no tie break in the second set if three sets have been played.
    """

    allsets = threesets_check_leadingzeroes(result_list)

    """
    Count sets and return the dictionary
    """

    sets_counted_dict = count_sets(allsets, player1, player2)

    return sets_counted_dict


def check_playerkey(player, keycheck, matches_dict, matchidx):
    """
    keycheck: 'Serve1stPCT_' or 'ReceivingPointsWonPCT_', etc.
    We want to check whether the player has been stored under 'Name_1' or 'Name_2' in the csv data
    """
    for playeridx in ['1', '2']:
        if player == matches_dict['Name_'+playeridx][matchidx]:
            playerkey = keycheck+playeridx
            return playerkey
    sys.exit("No stat key present in the dictionary!")


def add_new_player_to_db(players_dict, player_name):
    """
    :param players_dict: Players database dictionary
    :param player_name: Name of the player to add to the dictionary
    :return: Players database with one added player with clean stats
    """
    players_dict['Players'][player_name] = deepcopy(players_dict['template'])

    return None


def add_empty_match_to_db(name1, name2):
    empty_match_stats = {'prematch': {name1: {}, name2: {}}, 'postmatch': {name1: {}, name2: {}}, 'winner': None}
    return empty_match_stats


def open_cfg_asdict(path_to_config):
    with open(path_to_config, "r") as stream:
        try:
            cfg_dict = yaml.safe_load(stream)
            return cfg_dict
        except yaml.YAMLError as exc:
            print(exc)


def import_csv(file_path):
    df = read_csv(file_path).to_dict()
    return df
