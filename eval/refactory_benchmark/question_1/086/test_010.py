
from wrong_1_086 import *

import pytest
@pytest.mark.timeout(5)
def test_010():
    assert search(100, []) == 0
