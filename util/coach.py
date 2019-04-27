#!/usr/bin/env python3

import csv
import operator
import pprint
from collections import defaultdict
import random
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
    assert num_players >= 10
    possible_positions = outfield + infield + sitting
    positions_to_remove = ['Sit', 'RCF']
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
                for position_played in row[2:]:
                    assert position_played in get_possible_positions() or position_played == '', f"{position_played} is not a valid position"
                    player_game_array[name].append(position_played)
            line_count += 1

    return player_game_array


def decorate_frequencies_with_preferences(player_name, frequencies: List[Tuple[float, str]], last_position_played: str) -> List[Tuple[float, str, int]]:
    ret = []
    for frequency, position in frequencies:
        if last_position_played in outfield + sitting and position in infield:
            ret.append((frequency, position, 0))
        elif last_position_played in infield and position in outfield + sitting:
            ret.append((frequency, position, 0))
        else:
            ret.append((frequency, position, 1))
    return ret


def calculate_next_positions(player_game_array, all_players: Tuple[str], absents: Optional[Tuple[str, ...]] = None,
                             exclusions: Optional[Dict[str, Tuple[str]]] = None):
    players = list(remove_absents(absents, all_players))
    possible_positions = get_possible_positions(len(players))
    all_player_frequencies = get_player_position_frequencies(player_game_array, possible_positions)
    # pprint.pprint(all_player_frequencies)

    frequencies_list = []
    for player, frequencies in all_player_frequencies.items():
        last_position_played = player_game_array[player][-1]
        new_frequencies = decorate_frequencies_with_preferences(player, frequencies, last_position_played)
        new_frequencies.sort(key=operator.itemgetter(0, 2))
        frequencies_list.append((player, new_frequencies))

    frequencies_list.sort(key=lambda x: x[1][0])

    done = False
    new_assignments = None
    while not done:
        available_positions = list(possible_positions)
        # random.shuffle(players)
        new_assignments = []
        for frequency_line in frequencies_list:
            player = frequency_line[0]
            if player in absents:
                continue
            frequencies = frequency_line[1]
            # print('Looking for position for', player)
            # frequencies = all_player_frequencies[player]
            last_position_played = player_game_array[player][-1]
            # frequencies = decorate_frequencies_with_preferences(player, frequencies, last_position_played)
            # random.shuffle(frequencies)
            # print(f'  Frequencies for {player}: {frequencies}')
            # Sort first by the position that they have played the least, and second, trying to move from outfield to infield or vice versa
            # frequencies.sort(key=operator.itemgetter(0, 2))
            # print(f'  After sorting {player}: {frequencies}')
            good_possible_positions = [position for _, position, _ in frequencies if position in available_positions]
            if player in exclusions:
                for exclusion in exclusions[player]:
                    if exclusion in good_possible_positions:
                        good_possible_positions.remove(exclusion)
            # print(f'  Good_possible_positions: {good_possible_positions}')
            assigned_position = good_possible_positions[0]
            index = 1
            while assigned_position == last_position_played:
                print('Player playing same position again, trying again!')
                assigned_position = good_possible_positions[index]
                index += 1
            new_assignments.append((player, assigned_position))
            available_positions.remove(assigned_position)
        else:
            done = True

    return new_assignments


def remove_absents(absents: Tuple[str], players: Tuple[str]) -> Tuple[str]:
    players_copy = list(players)
    if absents:
        for absent in absents:
            players_copy.remove(absent)
    return tuple(players_copy)


def get_player_position_frequencies(player_game_array, possible_positions) -> Dict[str, List[Tuple[float, str]]]:
    all_player_frequencies = {}
    for player, positions_played in player_game_array.items():
        positions_played = [position_played for position_played in positions_played if position_played != '']
        frequencies_for_each_position = []
        for position in possible_positions:
            percentage_played_this_position = positions_played.count(position) / len(positions_played)
            frequencies_for_each_position.append((percentage_played_this_position, position))
        all_player_frequencies[player] = frequencies_for_each_position
    return all_player_frequencies


def add_new_positions_to_game_array(player_game_array, new_positions):
    for player, new_position in new_positions:
        player_game_array[player].append(new_position)
    return player_game_array


def write_player_game_array_to_csv():
    pass


def print_player_game_array(player_game_array):
    for player, list_of_positions_played in player_game_array.items():
        print(player + ' ' * (10 - len(player)), end='')
        for position in list_of_positions_played:
            print('\t', position + ' '*(5 - len(position)), end='')
        print()


def main():
    player_game_array = get_player_game_array('/home/david/Downloads/Grey Wolves Position Tracking - Positions.csv')
    print('Current positions played:')
    print_player_game_array(player_game_array)
    all_players = tuple(player_game_array.keys())
    for i in range(1, 6):
        print('*'*80)
        print(f'Inning {i}')
        print('*' * 80)
        new_positions = calculate_next_positions(player_game_array, all_players, absents=('Jodhyn',), exclusions={'Felix': ('C',)})
        # new_positions = calculate_next_positions(player_game_array, all_players)
        print(new_positions)

        player_game_array = add_new_positions_to_game_array(player_game_array, new_positions)
    print('New positions played:')
    print_player_game_array(player_game_array)

    all_player_frequencies = get_player_position_frequencies(player_game_array, get_possible_positions())
    pprint.pprint(all_player_frequencies)


if __name__ == '__main__':
    main()
