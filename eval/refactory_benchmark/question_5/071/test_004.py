import heapq

from wrong_5_071 import *

import pytest
@pytest.mark.timeout(5)
def test_004():
    assert top_k([4, 5, 2, 3, 1, 6], 3) == [6, 5, 4]
