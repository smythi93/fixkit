"""
The normalization module provides the necessary tools to normalize the weights of locations.
"""

from typing import List

from fixkit.localization.location import Weighted


def absolute_normalize(weighted_locations: List[Weighted]):
    """
    Normalize the weights of the locations by their absolute values and dividing with the maximum of the new weights.
    :param List[Weighted] weighted_locations: The locations to normalize.
    """
    maximum = max([abs(w.weight) for w in weighted_locations])
    for w in weighted_locations:
        w.weight = abs(w.weight) / maximum


def normalize(weighted_locations: List[Weighted]):
    """
    Normalize the weights of the locations by shifting the weights and dividing with the maximum of the new weights.
    :param List[Weighted] weighted_locations: The locations to normalize.
    """
    maximum, minimum = (
        max([w.weight for w in weighted_locations]),
        min([w.weight for w in weighted_locations]),
    )
    if minimum < 0:
        maximum = maximum - minimum
    else:
        minimum = 0
    for w in weighted_locations:
        w.weight = (w.weight - minimum) / maximum


__all__ = ["absolute_normalize", "normalize"]
