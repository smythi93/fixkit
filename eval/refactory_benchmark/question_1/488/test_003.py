
from wrong_1_488 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert search(5, (1, 5, 10)) == 1