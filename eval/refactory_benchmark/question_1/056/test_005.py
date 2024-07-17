
from wrong_1_056 import *

import pytest
@pytest.mark.timeout(5)
def test_005():
    assert search(3, (1, 5, 10)) == 1
