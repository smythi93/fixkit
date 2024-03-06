"""
The location module provides the necessary tools to represent a location in the source code.
"""

import abc
import math
from typing import Callable

from sflkit.analysis.suggestion import Location


class Weighted(abc.ABC):
    """
    An abstract class to represent a weighted object.
    """

    def __init__(self, weight: float):
        """
        Initialize the weighted object.
        :param float weight: The weight of the object.
        """
        self.weight = 0 if math.isnan(weight) else weight

    def __comp__(self, other, comp: Callable[[float, float], bool]):
        """
        Compare the weight of the object with another.
        :param other: The other object to compare with.
        :param Callable[[float, float], bool] comp: The comparison function.
        """
        return (
            comp(float(self.weight), other.weight)
            if hasattr(other, "weight")
            else NotImplemented
        )

    def __lt__(self, other):
        return self.__comp__(other, float.__lt__)

    def __le__(self, other):
        return self.__comp__(other, float.__le__)

    def __gt__(self, other):
        return self.__comp__(other, float.__gt__)

    def __ge__(self, other):
        return self.__comp__(other, float.__ge__)

    @abc.abstractmethod
    def __repr__(self):
        pass

    def __str__(self):
        return self.__repr__()


class WeightedLocation(Location, Weighted):
    """
    A class to represent a weighted location in the source code based on a file and a line number.
    """

    def __init__(self, file: str, line: int, weight: float):
        """
        Initialize the weighted location.
        :param str file: The file of the location.
        :param int line: The line number of the location.
        :param float weight: The weight of the location.
        """
        super().__init__(file, line)
        Weighted.__init__(self, weight)

    def __repr__(self):
        return f"{self.file}:{self.line}[{self.weight:.4f}]"


class WeightedIdentifier(Weighted):
    """
    A class to represent a weighted location in the source code based on a statement defined by the identifier.
    """

    def __init__(self, identifier: int, weight: float):
        """
        Initialize the weighted identifier.
        :param int identifier: The identifier of the location.
        :param float weight: The weight of the location.
        """
        super().__init__(weight)
        self.identifier = identifier

    def __repr__(self):
        return f"{self.identifier}[{self.weight:.4f}]"


__all__ = ["WeightedLocation", "WeightedIdentifier"]
