from collections import OrderedDict

from wrong_3_001 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert remove_extras([]) == []