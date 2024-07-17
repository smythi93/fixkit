
from wrong_1_006 import *

import pytest
@pytest.mark.timeout(5)
def test_010():
    assert search(100, []) == 0
