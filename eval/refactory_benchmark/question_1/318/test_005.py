
from wrong_1_318 import *

import pytest
@pytest.mark.timeout(5)
def test_005():
    assert search(3, (1, 5, 10)) == 1
