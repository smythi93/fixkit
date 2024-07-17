from collections import OrderedDict

from wrong_3_078 import *

import pytest
@pytest.mark.timeout(5)
def test_004():
    assert remove_extras([3, 4, 5, 1, 3]) == [3, 4, 5, 1]
