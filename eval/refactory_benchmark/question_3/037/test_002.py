from collections import OrderedDict

from wrong_3_037 import *

import pytest
@pytest.mark.timeout(5)
def test_002():
    assert remove_extras([1, 5, 1, 1, 3, 2]) == [1, 5, 3, 2]
