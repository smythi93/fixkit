
from wrong_4_038 import *

import pytest
@pytest.mark.timeout(5)
def test_004():
    assert sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30)]) == [('M', 30), ('M', 23), ('F', 19), ('F', 18)]
