import unittest
from xharvest import Hour


class HourConversionTestCase(unittest.TestCase):

    def test_hour(self):
        h = Hour('1.00')
        self.assertEqual(h.value, 3600)
        self.assertEqual(h.as_harvest_str(), '1.00')

    def test_hour_tweentyfive(self):
        h = Hour('1.25')
        self.assertEqual(h.value, 4500)
        self.assertEqual(h.as_harvest_str(), '1.25')

    def test_hour_an_half(self):
        h = Hour('1.50')
        self.assertEqual(h.value, 5400)
        self.assertEqual(h.as_harvest_str(), '1.50')
