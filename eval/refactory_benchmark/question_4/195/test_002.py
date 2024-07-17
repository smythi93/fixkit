
from wrong_4_195 import *

import pytest
@pytest.mark.timeout(5)
def test_002():
    assert sort_age([("M", 35), ("F", 18), ("M", 23), ("F", 19), ("M", 30), ("M", 17)]) == [('M', 35), ('M', 30), ('M', 23), ('F', 19), ('F', 18), ('M', 17)]
