import unittest
import todoflow.colors as colors


class ColorsTest(unittest.TestCase):
    red = '\033[31m'
    defc = '\033[0m'

    def test_constants(self):
        self.assertTrue(colors.red)
        self.assertEquals(colors.RED, self.red)

    def test_functions(self):
        text = colors.red('text')
        self.assertTrue(text.startswith(self.red))
        self.assertTrue(text.endswith(self.defc))

    def test_doesnt_add_unnecassary_defc(self):
        text = colors.red('text')
        self.assertFalse(colors.blue(text).endswith(self.defc + self.defc))


def print_colors():
    for k in colors.foreground_codes:
        print getattr(colors, k)('this is ' + k)
    for k in colors.background_codes:
        print getattr(colors, 'on_' + k)('this is on ' + k)
    for fk in colors.foreground_codes:
        for bk in colors.background_codes:
            print getattr(colors, fk + '_on_' + bk)('this is ' + fk + ' on ' + bk)


if __name__ == '__main__':
    print_colors()
    unittest.main()
