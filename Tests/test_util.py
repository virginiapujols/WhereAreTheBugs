from unittest import TestCase
from Util import Util

class TestUtil(TestCase):
    def test_normalization_zero_division(self):
        self.assertRaises(ZeroDivisionError,Util.normalization,1,1,1)

    def test_normalization_max_less_than_min(self):
        self.assertRaises(ArithmeticError, Util.normalization,1,-2,1)


