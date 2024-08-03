from django.test import TestCase
from membership.utils import *

import datetime

class GetEndDateTests(TestCase):
    def test_same_year_beginning(self):
        date = datetime.datetime(2000, 1, 1)
        self.assertEqual(get_end_date(date), datetime.datetime(2000, 9, 30))

    def test_same_year_middle(self):
        date = datetime.datetime(2000, 2, 28)
        self.assertEqual(get_end_date(date), datetime.datetime(2000, 9, 30))

    def test_same_year_end(self):
        date = datetime.datetime(2000, 4, 30)
        self.assertEqual(get_end_date(date), datetime.datetime(2000, 9, 30))

    def test_next_year_start(self):
        date = datetime.datetime(2000, 5, 1)
        self.assertEqual(get_end_date(date), datetime.datetime(2001, 9, 30))

    def test_next_year_middle(self):
        date = datetime.datetime(2000, 6, 30)
        self.assertEqual(get_end_date(date), datetime.datetime(2001, 9, 30))

    def test_sept_30(self):
        date = datetime.datetime(2000, 9, 30)
        self.assertEqual(get_end_date(date), datetime.datetime(2001, 9, 30))

    def test_next_year_end(self):
        date = datetime.datetime(2000, 12, 31)
        self.assertEqual(get_end_date(date), datetime.datetime(2001, 9, 30))