
from wrong_1_377 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert search(5, (1, 5, 10)) == 1