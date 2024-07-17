from collections import OrderedDict

from wrong_3_263 import *

import pytest
@pytest.mark.timeout(5)
def test_003():
    assert remove_extras([]) == []
