
from wrong_1_431 import *

import pytest
@pytest.mark.timeout(5)
def test_002():
    assert search(42, [1, 5, 10]) == 3
