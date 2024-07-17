
from wrong_1_098 import *

import pytest
@pytest.mark.timeout(5)
def test_010():
    assert search(100, []) == 0
