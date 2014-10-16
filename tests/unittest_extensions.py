import unittest


class SeriesTestCase(unittest.TestCase):
    def conduct_test_series(self, assert_function, values):
        for v in values:
            assert_function(*v)
