
from wrong_1_481 import *

import pytest
@pytest.mark.timeout(5)
def test_001():
    assert search(42, (-5, 1, 3, 5, 7, 10)) == 6
