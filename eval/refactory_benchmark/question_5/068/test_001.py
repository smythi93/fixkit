import heapq

from wrong_5_068 import *

import pytest
@pytest.mark.timeout(5)
def test_001():
    assert top_k([9, 9, 4, 9, 7, 9, 3, 1, 6], 5) == [9, 9, 9, 9, 7]
