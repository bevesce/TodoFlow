import unittest
import datetime

from todoflow.parse_date import parse_date


date = datetime.datetime(2016, 10, 4, 22, 39)


class TestParseDate(unittest.TestCase):
    def assertDate(self, date, date_string):
        self.assertEqual(date.strftime('%F'), date_string)

    def assertDatetime(self, date, date_string):
        self.assertEqual(date.strftime('%F %R'), date_string)

    def test_01(self):
        self.assertDate(parse_date('jan', date), '2016-01-01')

    def test_02(self):
        self.assertDate(parse_date('mon', date), '2016-10-03')

    def test_03(self):
        self.assertDate(parse_date('next mon', date), '2016-10-10')

    def test_04(self):
        self.assertDate(parse_date('last mon', date), '2016-09-26')

    def test_05(self):
        self.assertDate(parse_date('last mon + 1day', date), '2016-09-27')

    def test_06(self):
        self.assertDate(parse_date('2016', date), '2016-01-01')

    def test_07(self):
        self.assertDate(parse_date('today 1day', date), '2016-10-05')

    def test_08(self):
        self.assertDate(parse_date('today -1day', date), '2016-10-03')

    def test_09(self):
        self.assertDate(parse_date('today 1year', date), '2017-10-04')

    def test_10(self):
        self.assertDate(parse_date('2016-05', date), '2016-05-01')

    def test_11(self):
        self.assertDate(parse_date('2016-05-13years', date), '2016-05-13')

    def test_12(self):
        self.assertDate(parse_date('today + 1 week', date), '2016-10-11')

    def test_13(self):
        self.assertDate(parse_date('sun', date), '2016-10-09')

    def test_14(self):
        self.assertDate(parse_date('fri', date), '2016-10-07')

    def test_15(self):
        self.assertDate(parse_date('2016', date), '2016-01-01')

    def test_16(self):
        self.assertDate(parse_date('today +1month', date), '2016-11-04')

    def test_17(self):
        self.assertDate(parse_date('2016-12-1 +1month', date), '2017-01-01')

    def test_18(self):
        self.assertDate(parse_date('2016-12-1 +28month', date), '2019-04-01')

    def test_19(self):
        self.assertDate(parse_date('next week', date), '2016-10-10')

    def test_20(self):
        self.assertDate(parse_date('next may', date), '2017-05-01')

    def test_20(self):
        self.assertDate(parse_date('last may', date), '2015-05-01')

    def test_21(self):
        self.assertDate(parse_date('next day', date), '2016-10-05')

    def test_22(self):
        self.assertDate(parse_date('next month', date), '2016-11-01')

    def test_23(self):
        self.assertDate(parse_date('next year', date), '2017-01-01')

    def test_24(self):
        self.assertDatetime(parse_date('now', date), '2016-10-04 22:39')

    def test_25(self):
        self.assertDatetime(parse_date('next hour', date), '2016-10-04 23:00')

    def test_26(self):
        self.assertDatetime(parse_date('next min', date), '2016-10-04 22:40')

    def test_27(self):
        self.assertDatetime(parse_date('last min', date), '2016-10-04 22:38')

    def test_28(self):
        self.assertDatetime(parse_date('', date), '2016-10-04 22:39')

    def test_30(self):
        self.assertDatetime(parse_date('10:35 am', date), '2016-10-04 10:35')

    def test_31(self):
        self.assertDatetime(parse_date('10:35 pm', date), '2016-10-04 22:35')

    def test_32(self):
        self.assertDatetime(parse_date('12:00 pm', date), '2016-10-04 12:00')

    def test_33(self):
        self.assertDatetime(parse_date('12:05 am', date), '2016-10-04 00:05')

    def test_34(self):
        self.assertDatetime(parse_date('12 am', date), '2016-10-04 00:00')

if __name__ == '__main__':
    unittest.main()
