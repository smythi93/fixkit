
from wrong_1_023 import *

import pytest
@pytest.mark.timeout(5)
def test_006():
    assert search(-5, (1, 5, 10)) == 0