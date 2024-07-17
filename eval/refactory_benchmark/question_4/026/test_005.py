
from wrong_4_026 import *

import pytest
@pytest.mark.timeout(5)
def test_005():
    assert sort_age([("M", 23), ("F", 19), ("M", 30)]) == [('M', 30), ('M', 23), ('F', 19)]
