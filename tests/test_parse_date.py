import unittest

from todoflow.parse_date import Lexer
from todoflow.parse_date import iterate_parts


print(Lexer().tokenize('2014-12 jan week'))




class TestTypes(unittest.TestCase):
    def parts(self, l, size):
        self._parts = iterate_parts(l, 3)
        return self

    def are(self, l):
        self.assertEqual(list(self._parts), l)

    def test_1(self):
        self.parts([1, 2, 3], 3).are([[1, 2, 3]])

    def test_2(self):
        self.parts([1, 2, 3, 4], 3).are([[1, 2, 3], [2, 3, 4]])


if __name__ == '__main__':
    unittest.main()
