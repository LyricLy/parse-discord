import unittest
import datetime

from parse_discord import *


zero = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)
neg = datetime.datetime.fromtimestamp(-1, datetime.timezone.utc)

class Time(unittest.TestCase):
    def test_time(self):
        self.assertEqual(parse("<t:0:R>"), Markup([Timestamp(zero, "R")]))

    def test_default(self):
        self.assertEqual(parse("<t:0>"), Markup([Timestamp(zero, "f")]))

    def test_bad_format(self):
        self.assertEqual(parse("<t:0:r>"), Markup([Text("<t:0:r>")]))

    def test_negative_time(self):
        self.assertEqual(parse("<t:-1>"), Markup([Timestamp(neg, "f")]))
