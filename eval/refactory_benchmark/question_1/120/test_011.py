
from wrong_1_120 import *

import pytest
@pytest.mark.timeout(5)
def test_011():
    assert search(-100, ()) == 0
