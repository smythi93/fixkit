from collections import OrderedDict

from wrong_3_273 import *

import pytest
@pytest.mark.timeout(5)
def test_001():
    assert remove_extras([1, 1, 1, 2, 3]) == [1, 2, 3]
