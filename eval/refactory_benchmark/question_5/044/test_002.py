import heapq

from wrong_5_044 import *

import pytest
@pytest.mark.timeout(5)
def test_002():
    assert top_k([9, 8, 4, 5, 7, 2, 3, 1, 6], 5) == [9, 8, 7, 6, 5]
