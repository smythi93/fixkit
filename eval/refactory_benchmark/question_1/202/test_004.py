
from wrong_1_202 import *

import pytest
@pytest.mark.timeout(5)
def test_004():
    assert search(7, [1, 5, 10]) == 2
