from pandas.util.py3compat import StringIO, BytesIO
from datetime import date, datetime
import csv
import os
import sys
import re
import unittest

import nose

from numpy import nan
import numpy as np
from numpy.testing.decorators import slow

from pandas import DataFrame, Series, Index, isnull
import pandas.io.parsers as parsers
from pandas.io.parsers import (read_csv, read_table, read_fwf,
                               ExcelFile, TextParser)
from pandas.util.testing import (assert_almost_equal, assert_frame_equal,
                                 assert_series_equal, network)
import pandas.lib as lib
from pandas.util import py3compat
from pandas.lib import Timestamp
import pandas.io.date_converters as conv

class TestConverters(unittest.TestCase):

    def setUp(self):
        self.years = np.array([2007, 2008])
        self.months = np.array([1, 2])
        self.days = np.array([3, 4])
        self.hours = np.array([5, 6])
        self.minutes = np.array([7, 8])
        self.seconds = np.array([9, 0])
        self.dates = np.array(['2007/1/3', '2008/2/4'], dtype=object)
        self.times = np.array(['05:07:09', '06:08:00'], dtype=object)
        self.expected = np.array([datetime(2007, 1, 3, 5, 7, 9),
                                  datetime(2008, 2, 4, 6, 8, 0)])

    def test_parse_date_time(self):
        result = conv.parse_date_time(self.dates, self.times)
        self.assert_((result == self.expected).all())

        data = """\
date, time, a, b
2001-01-05, 10:00:00, 0.0, 10.
2001-01-05, 00:00:00, 1., 11.
"""
        datecols = {'date_time': [0, 1]}
        df = read_table(StringIO(data), sep=',', header=0,
                        parse_dates=datecols, date_parser=conv.parse_date_time)
        self.assert_('date_time' in df)
        self.assert_(df.date_time.ix[0] == datetime(2001, 1, 5, 10, 0, 0))

        data =  ("KORD,19990127, 19:00:00, 18:56:00, 0.8100\n"
                 "KORD,19990127, 20:00:00, 19:56:00, 0.0100\n"
                 "KORD,19990127, 21:00:00, 20:56:00, -0.5900\n"
                 "KORD,19990127, 21:00:00, 21:18:00, -0.9900\n"
                 "KORD,19990127, 22:00:00, 21:56:00, -0.5900\n"
                 "KORD,19990127, 23:00:00, 22:56:00, -0.5900")

        date_spec = {'nominal': [1, 2], 'actual': [1, 3]}
        df = read_csv(StringIO(data), header=None, parse_dates=date_spec,
                 date_parser=conv.parse_date_time)

    def test_parse_date_fields(self):
        result = conv.parse_date_fields(self.years, self.months, self.days)
        expected = np.array([datetime(2007, 1, 3), datetime(2008, 2, 4)])
        self.assert_((result == expected).all())

        data = "year, month, day, a\n 2001 , 01 , 10 , 10.\n 2001 , 02 , 1 , 11."
        datecols = {'ymd': [0, 1, 2]}
        df = read_table(StringIO(data), sep=',', header=0,
                        parse_dates=datecols,
                        date_parser=conv.parse_date_fields)
        self.assert_('ymd' in df)
        self.assert_(df.ymd.ix[0] == datetime(2001, 1, 10))

    def test_datetime_six_col(self):
        result = conv.parse_all_fields(self.years, self.months, self.days,
                                       self.hours, self.minutes, self.seconds)
        self.assert_((result == self.expected).all())

        data = """\
year, month, day, hour, minute, second, a, b
2001, 01, 05, 10, 00, 0, 0.0, 10.
2001, 01, 5, 10, 0, 00, 1., 11.
"""
        datecols = {'ymdHMS': [0, 1, 2, 3, 4, 5]}
        df = read_table(StringIO(data), sep=',', header=0,
                        parse_dates=datecols,
                        date_parser=conv.parse_all_fields)
        self.assert_('ymdHMS' in df)
        self.assert_(df.ymdHMS.ix[0] == datetime(2001, 1, 5, 10, 0, 0))

    def test_generic(self):
        data = "year, month, day, a\n 2001, 01, 10, 10.\n 2001, 02, 1, 11."
        datecols = {'ym': [0, 1]}
        dateconverter = lambda y, m: date(year=int(y), month=int(m), day=1)
        df = read_table(StringIO(data), sep=',', header=0,
                        parse_dates=datecols,
                        date_parser=dateconverter)
        self.assert_('ym' in df)
        self.assert_(df.ym.ix[0] == date(2001, 1, 1))


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],
                   exit=False)
