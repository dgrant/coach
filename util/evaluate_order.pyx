# cython: language_level=3

import cython
from random import random
from typing import List
from libc.stdlib cimport rand

def evaluate_order_c(batting_order: List[float],
                    num_innings: int,
                    run_limits: List[int],
                    num_batters: int) -> int:
    return _evaluate_order_c(batting_order, num_innings, run_limits, num_batters)

@cython.cdivision(True)
cdef _evaluate_order_c(list batting_order,
                    int num_innings,
                    list run_limits,
                    int num_batters):
    cdef int order_position, runs_scored, num_on_base, num_outs, runs_limit_for_inning
    cdef double rand_value, obs_percentage
    order_position = 0
    runs_scored = 0
    for inning in range(num_innings):
        num_on_base = 0
        num_outs = 0
        runs_limit_for_inning = run_limits[inning]
        while num_outs < 3 and runs_scored < runs_limit_for_inning:
            order_position += 1
            order_position = order_position % num_batters
            obs_percentage = batting_order[order_position]
            rand_value = random()
            if rand_value < obs_percentage:
                # Got hit
                num_on_base += 1
                if num_on_base > 3:
                    runs_scored += 1
            else:
                num_outs += 1
    return runs_scored
