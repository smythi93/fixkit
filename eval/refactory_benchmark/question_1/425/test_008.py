
from wrong_1_425 import *

import pytest
@pytest.mark.timeout(5)
def test_008():
    assert search(-100, (-5, -1, 3, 5, 7, 10)) == 0
