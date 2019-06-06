#!/usr/bin/env python3

import csv
import operator
import pprint
import random
import sys
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

infield = [
    'C',
    'P',
    '1B',
    '2B',
    '3B',
    'SS',
    'Rover',
]

outfield = [
    'LF',
    'LCF',
    'RF',
    'RCF',
]

sitting = [
    'Sit',
]


def get_possible_positions(num_players=12):
    assert num_players <= 12
    assert num_players >= 9
    possible_positions = outfield + infield + sitting
    positions_to_remove = ['Sit', 'RCF', 'LCF', ]
    num_to_remove = len(possible_positions) - num_players
    positions_to_remove = positions_to_remove[:num_to_remove]
    for position_to_remove in positions_to_remove:
        possible_positions.remove(position_to_remove)
    return tuple(possible_positions)


def get_player_game_array(csv_file) -> Dict[str, List[str]]:
    player_game_array = defaultdict(list)
    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # dates
                pass
            elif line_count == 1:
                # inning
                pass
            elif line_count == 14:
                break
            else:
                name = row[0]
                for position_played in row[3:]:
                    assert (
                        position_played in get_possible_positions()
                        or position_played == ""
                    ), f"{position_played} is not a valid position"
                    player_game_array[name].append(position_played)
            line_count += 1

    return player_game_array


def decorate_frequencies_with_preferences(player_name, frequencies: List[Tuple[float, str]],
                                          last_positions_played: List[str],
                                          outfield_percentages: List[Tuple[str, float]],
                                          players_who_need_to_sit: List[str]) -> List[Tuple[float, str, int]]:
    guys_who_played_in_outfield_most = [player for (player, _) in outfield_percentages][-int(len(outfield_percentages) / 3):]
    ret = []
    for frequency, position in frequencies:
        score = 0

        if last_positions_played[-1] in outfield + sitting and position in infield:
            # If they were in the outfield or sitting last, then new position is infield, this is good
            score = 0
        elif last_positions_played[-1] in infield and position in outfield + sitting:
            # If they were in the outfield or sitting last, then new position is infield, this is good
            score = 0
        else:
            # Otherwise, not good, we don't want in infield twice in a row or outfield twice in a row
            score += 1

        if player_name in guys_who_played_in_outfield_most and position in outfield:
            score += 1

        if player_name not in players_who_need_to_sit and position in sitting:
            score += 1

        # Bad if they are playing the same position again if they already played it in last few innings
        score += last_positions_played.count(position)

        ret.append((frequency, position, score))
    return ret


def _get_sit_percentages(player_game_array):
    sit_percentages = []
    for player, positions_played in player_game_array.items():
        positions_played = [position_played for position_played in positions_played if position_played != '']
        sit_percentages.append((player, positions_played.count('Sit') / len(positions_played)))
    random.shuffle(sit_percentages)
    sit_percentages.sort(key=operator.itemgetter(1))
    return sit_percentages


def _get_outfield_percentages(player_game_array):
    outfield_percentages = []
    for player, positions_played in player_game_array.items():
        positions_played = [position_played for position_played in positions_played if position_played != '']
        num_in_outfield = 0
        for position in outfield:
            num_in_outfield += positions_played.count(position)
        outfield_percentages.append((player, num_in_outfield / len(positions_played)))
    random.shuffle(outfield_percentages)
    outfield_percentages.sort(key=operator.itemgetter(1))
    return outfield_percentages


def get_players_who_need_to_sit(sitting_percentages):
    minimum = min([percent for _, percent in sitting_percentages])
    return [player for player, percent in sitting_percentages if percent == minimum]


def calculate_next_positions(player_game_array, all_players: Tuple[str], absents: Optional[Tuple[str, ...]] = None,
                             exclusions: Optional[Dict[str, Tuple[str]]] = None):
    done = False

    kid_to_put_first = None
    players = tuple(remove_absents(absents, all_players))
    possible_positions = get_possible_positions(len(players))
    outfield_percentages, sitting_percentages = get_sitting_and_outfield_percentages(player_game_array)
    players_who_need_to_sit = get_players_who_need_to_sit(sitting_percentages)
    all_player_frequencies = get_player_position_frequencies(player_game_array, possible_positions)

    frequencies_list = []
    for player, frequencies in all_player_frequencies.items():
        if player in exclusions:
            frequencies = [(frequency, position) for frequency, position in frequencies if
                           position not in exclusions[player]]
        # Get the last 3 positions played (ignore empty cells which means the player was absent)
        last_positions_played = [x for x in player_game_array[player] if x != ''][-3:]
        new_frequencies = decorate_frequencies_with_preferences(player, frequencies, last_positions_played,
                                                                outfield_percentages, players_who_need_to_sit)
        # Sort by preference first (so they aren't in the outfield twice in a row), then frequency
        new_frequencies.sort(key=operator.itemgetter(2, 0))
        frequencies_list.append([player, new_frequencies])
    MAX_TRIES = 100
    tries = 0
    while not done and tries < MAX_TRIES:
        tries += 1
        available_positions = list(possible_positions)
        new_assignments = []
        print('SHUFFLING')
        random.shuffle(frequencies_list)
        # Sort first by the frequency and then by the player preference
        # frequencies_list.sort(key=lambda x: (x[1][0][0], x[1][0][2]))
        # if kid_to_put_first:
        #     index = [x[0] for x in frequencies_list].index(kid_to_put_first)
        #     frequencies_list = [frequencies_list[index]] + frequencies_list[:index] + frequencies_list[index + 1:]

        for frequency_line in frequencies_list:
            player = frequency_line[0]
            last_positions_played = [x for x in player_game_array[player] if x != ''][-3:]
            if absents and player in absents:
                new_assignments.append((player, ''))
                continue
            frequencies = frequency_line[1]
            last_position_played = player_game_array[player][-1]
            good_possible_positions = [position for _, position, _ in frequencies if position in available_positions]

            # Remove excluded positions from good_possible_positions
            if player in exclusions:
                for exclusion in exclusions[player]:
                    if exclusion in good_possible_positions:
                        good_possible_positions.remove(exclusion)
            if len(good_possible_positions) == 0:
                # Probably because this player has an exclusion and his excluded position is the only available position
                # left in this inning. Try again.
                print(f'No position available for {player}... trying again')
                # kid_to_put_first = player
                break
            assigned_position = good_possible_positions[0]
            if assigned_position == 'Sit' and player not in players_who_need_to_sit:
                # Only sit the guy who has sat the least
                print(f'This player has sat too much: {player}')
                break
            if assigned_position in outfield:
                last_position = [x for x in player_game_array[player] if x != ''][-1]
                if last_position in outfield:
                    # Don't allow outfield twice in a row
                    print(f'This player can\'t play outfield twice in a row: {player}')
                    break
            if assigned_position in outfield and player in [player for player, _ in outfield_percentages][
                                                           -int(len(outfield_percentages) / 3):]:
                # If this player has played outfield a lot, don't again
                print(f'This player has played outfield lots this year: {player}')
                break
            if assigned_position in last_positions_played and assigned_position in infield:
                # Don't play the same position again too soon
                print(f'This player can\'t play same infield position {assigned_position} too soon: {player}')
                break
            # if assigned_position == last_position_played and len(good_possible_positions) > 1:
            #     Take the next option available
            # assigned_position = good_possible_positions[1]
            # elif assigned_position == last_position_played and len(good_possible_positions) == 1:
            #     There were no other options
            # print('Trying again!')
            # kid_to_put_first = player
            # break
            print(f'Assigning {player} to {assigned_position}')
            new_assignments.append((player, assigned_position))
            available_positions.remove(assigned_position)
        else:
            done = True
    if tries == MAX_TRIES:
        raise Exception('Failed to make roster')
    return new_assignments


def get_sitting_and_outfield_percentages(player_game_array):
    outfield_percentages = _get_outfield_percentages(player_game_array)
    sitting_percentages = _get_sit_percentages(player_game_array)
    print("outfield_percentages=\n" + pprint.pformat(outfield_percentages))
    print("sit_percentages=\n" + pprint.pformat(sitting_percentages))
    return outfield_percentages, sitting_percentages


def remove_absents(absents: Tuple[str], players: Tuple[str]) -> Tuple[str]:
    players_copy = list(players)
    if absents:
        for absent in absents:
            players_copy.remove(absent)
    return tuple(players_copy)


def get_player_position_frequencies(player_game_array, possible_positions) -> Dict[str, List[Tuple[float, str]]]:
    all_player_frequencies = {}
    for player, positions_played in player_game_array.items():
        print('Player:', player)
        positions_played = [position_played for position_played in positions_played if position_played != '']
        frequencies_for_each_position = []
        for position in possible_positions:
            print(f"{position}: {positions_played.count(position)}, ", end='')
            percentage_played_this_position = positions_played.count(position) / len(positions_played)
            frequencies_for_each_position.append((percentage_played_this_position, position))
        all_player_frequencies[player] = frequencies_for_each_position
        print()
    print()
    return all_player_frequencies


def add_new_positions_to_game_array(player_game_array, new_positions):
    for player, new_position in new_positions:
        player_game_array[player].append(new_position)
    return player_game_array


def write_player_game_array_to_csv():
    pass


def print_player_game_array(player_game_array, new=0):
    for player, list_of_positions_played in player_game_array.items():
        print(player + ' ' * (10 - len(player)), end='')
        for i, position in enumerate(list_of_positions_played):
            if i == len(list_of_positions_played) - new:
                print('\t*', position + ' ' * (5 - len(position)), end='')
            else:
                print('\t', position + ' ' * (5 - len(position)), end='')
        print()


def main():
    player_game_array = get_player_game_array('/home/david/Downloads/Grey Wolves Position Tracking - Positions.csv')
    print('Current positions played:')
    print_player_game_array(player_game_array)
    all_players = tuple(player_game_array.keys())
    all_player_frequencies = get_player_position_frequencies(player_game_array, get_possible_positions())
    pprint.pprint(all_player_frequencies)
    num_innings = 1
    for i in range(1, 1 + num_innings):
        print("*" * 80)
        print(f"Inning {i}")
        print("*" * 80)
        exclusions = {
            "Felix": ("C", ),
            "Jodhyn": ("1B", "C"),
            # "Piper": ("1B",),
            # "Zayne": ("1B",),
            # "Casey": ("1B",),
            # "Aiden": ("1B",),
            "Isaiah": ("Sit",),
            "Naden": ("Sit",),
            "Claire": ("Sit",),
            "Sam": ("Sit",),
        }
        absents = None
        new_positions = calculate_next_positions(
            player_game_array, all_players, absents=absents, exclusions=exclusions
        )
        print("New positions:", new_positions)

        player_game_array = add_new_positions_to_game_array(player_game_array, new_positions)

    get_sitting_and_outfield_percentages(player_game_array)
    all_player_frequencies = get_player_position_frequencies(player_game_array, get_possible_positions())
    pprint.pprint(all_player_frequencies)
    print('\nNew positions played:')
    print_player_game_array(player_game_array, new=num_innings)


if __name__ == '__main__':
    seed = random.randrange(sys.maxsize)
    # seed = 4844073752976889310
    random.seed(seed)
    main()
    print("Seed was:", seed)
