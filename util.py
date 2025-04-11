import math
from collections import Counter
from itertools import product

from constants import HEX_SIZE, CENTER_X, CENTER_Y

def hex_to_pixel(q, r):
    x = HEX_SIZE * (math.sqrt(3) * q + (math.sqrt(3) / 2) * r)
    y = HEX_SIZE * (3 / 2 * r)

    return CENTER_X + x, CENTER_Y + y

def snap(px, py, digits=3):
    return round(px, digits), round(py, digits)

ROLL_PROBABILITIES = {}

def estimate_roll_probability(roll):
    """
    Estimate the probability of rolling a specific total with fair dice. Uses cache values for optimizations.

    :param roll: The number to roll (i.e. 6, or 12)
    :return: The probability as a decimal.
    """
    if roll in ROLL_PROBABILITIES:
        return ROLL_PROBABILITIES[roll]

    # Generate all possible roll combinations.
    outcomes = list(product(range(1, 6 + 1), repeat=2))
    total_counts = Counter(sum(outcome) for outcome in outcomes)

    total_possibilities = len(outcomes)
    probability = total_counts[roll] / total_possibilities if roll in total_counts else 0.0
    ROLL_PROBABILITIES[roll] = probability
    return probability
