
from wrong_1_023 import *

import pytest
@pytest.mark.timeout(5)
def test_009():
    assert search(0, (-5, -1, 3, 5, 7, 10)) == 2
