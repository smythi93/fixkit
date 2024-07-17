
from wrong_1_550 import *

import pytest
@pytest.mark.timeout(5)
def test_011():
    assert search(-100, ()) == 0
