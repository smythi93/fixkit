import heapq

from wrong_5_061 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert top_k([4, 5, 2, 3, 1, 6], 6) == [6, 5, 4, 3, 2, 1]
