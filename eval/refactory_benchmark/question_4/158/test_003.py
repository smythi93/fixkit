
from wrong_4_158 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert sort_age([("F", 18), ("M", 23), ("F", 19), ("M", 30), ("M", 17)]) == [('M', 30), ('M', 23), ('F', 19), ('F', 18), ('M', 17)]
