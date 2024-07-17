
from wrong_1_119 import *

import pytest
@pytest.mark.timeout(5)
def test_007():
    assert search(10, (-5, -1, 3, 5, 7, 10)) == 5
