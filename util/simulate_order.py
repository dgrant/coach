import itertools
import statistics
import time
import random
from typing import Dict, List

# import numpy
# from util.evaluate_order import evaluate_order_c


def generate_all_combinations_of_orders(players: List[str]):
    # return itertools.permutations(players, len(players))
    # return numpy.random.permutation(players)
    while True:
        new_players = players[:]
        random.shuffle(new_players)
        yield new_players


def evaluate_order_python(batting_averages, num_innings: int, run_limits: List[int], num_batters: int):
    order_position = 0
    runs_scored = 0
    for inning in range(num_innings):
        num_on_base = 0
        num_outs = 0
        runs_limit_for_inning = run_limits[inning]
        while num_outs < 3 and runs_scored < runs_limit_for_inning:
            order_position += 1
            order_position = order_position % num_batters
            obs_percentage = batting_averages[order_position]
            if random.random() < obs_percentage:
                # Got hit
                num_on_base += 1
                if num_on_base > 3:
                    runs_scored += 1
            else:
                num_outs += 1
    return runs_scored


def find_best_permutation(obs_stats_dict: Dict[str, float], num_innings: int, run_limits: List[int], num_batters: int):
    players = list(obs_stats_dict.keys())
    start = time.time()
    best_runs_mean = 0
    for permutation in generate_all_combinations_of_orders(players):
        mean_runs, stddev = measure_permutation_averaged(obs_stats_dict, permutation, num_innings, run_limits, num_batters)
        if mean_runs > best_runs_mean:
            best_permutation = permutation
            best_runs_mean = mean_runs
            best_runs_stddev = stddev
            print_best_permutation(obs_stats_dict, best_runs_mean, best_runs_stddev, best_permutation)
    print('Took: {0}s'.format(time.time() - start))


def measure_permutation_averaged(obs_stats_dict, permutation, num_innings: int, run_limits: List[int], num_batters: int, tries=100):
    runs = []
    for i in range(tries):
        runs.append(evaluate_order_python([obs_stats_dict[batter] for batter in permutation], num_innings, run_limits, num_batters))
        # runs.append(evaluate_order_c([obs_stats_dict[batter] for batter in permutation], num_innings, run_limits, num_batters))
    mean_runs = statistics.mean(runs)
    stddev = statistics.stdev(runs)
    return mean_runs, stddev


def print_best_permutation(obs_stats_dict, best_average_runs, best_runs_stddev, best_permutation):
    print('Best permutation so far is:')
    for batter in best_permutation:
        print('{0}: {1}'.format(batter, obs_stats_dict[batter]))
    print('Num runs: {:.3f}'.format(best_average_runs))
    print('Stddev: {:.3f}'.format(best_runs_stddev))


if __name__ == '__main__':
    run_limits = [2, 2, 4, 4, 999]
    num_innings = 5
    obs_stats = (
        ("Felix", 0.259),
        ("Zayne", 0.320),
        ("Jodhyn", 0.286),
        ("Aiden", 0.333),
        ("William", 0.419),
        ("Casey", 0.360),
        ("Piper", 0.571),
        ("Sam", 0.581),
        ("Caleb", 0.586),
        ("Claire", 0.710),
        ("Isaiah", 0.774),
        ("Naden", 0.871),
    )
    obs_stats_dict = dict(obs_stats)
    # from util.simulate_order_c import find_best_permutation_c
    # find_best_permutation_c(obs_stats_dict, num_innings, run_limits)
    find_best_permutation(obs_stats_dict, num_innings, run_limits, len(obs_stats_dict))
