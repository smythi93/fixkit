
from wrong_1_007 import *

import pytest
@pytest.mark.timeout(5)
def test_007():
    assert search(10, (-5, -1, 3, 5, 7, 10)) == 5
