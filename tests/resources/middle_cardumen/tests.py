import unittest
from middle import middle


class MiddleTestCase(unittest.TestCase):
    def test_middle_335(self):
        self.assertEqual(3, middle(3, 3, 5))

    def test_middle_123(self):
        self.assertEqual(2, middle(1, 2, 3))

    def test_middle_321(self):
        self.assertEqual(2, middle(3, 2, 1))

    def test_middle_555(self):
        self.assertEqual(5, middle(5, 5, 5))

    def test_middle_534(self):
        self.assertEqual(4, middle(5, 3, 4))

    def test_middle_213(self):
        self.assertEqual(2, middle(2, 1, 3))
