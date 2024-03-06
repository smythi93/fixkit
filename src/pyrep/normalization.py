from typing import List

from pyrep.localization import WeightedLocation


def absolute_normalize(weighted_locations: List[WeightedLocation]):
    maximum = max([abs(w.weight) for w in weighted_locations])
    for w in weighted_locations:
        w.weight = abs(w.weight) / maximum


def normalize(weighted_locations: List[WeightedLocation]):
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
