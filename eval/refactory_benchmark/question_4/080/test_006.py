
from wrong_4_080 import *

import pytest
@pytest.mark.timeout(5)
def test_006():
    assert sort_age([]) == []
