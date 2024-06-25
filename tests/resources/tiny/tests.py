import unittest
from tiny import f


class MiddleTestCase(unittest.TestCase):
    def test_0(self):
        self.assertTrue(f(0))

    def test_2(self):
        self.assertFalse(f(2))

    def test_neg_3(self):
        self.assertTrue(f(-3))

    def test_neg_2(self):
        self.assertTrue(f(-2))
