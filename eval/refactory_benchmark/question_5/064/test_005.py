import heapq

from wrong_5_064 import *

import pytest
@pytest.mark.timeout(5)
def test_005():
    assert top_k([4, 5, 2, 3, 1, 6], 0) == []
