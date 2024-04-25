import unittest
import datetime

from parse_discord import *


class Time(unittest.TestCase):
    def test_time(self):
        self.assertEqual(parse("<t:0:R>"), Markup([Timestamp(0, "R")]))

    def test_default(self):
        self.assertEqual(parse("<t:0>"), Markup([Timestamp(0, "f")]))

    def test_bad_format(self):
        self.assertEqual(parse("<t:0:r>"), Markup([Text("<t:0:r>")]))

    def test_negative_time(self):
        self.assertEqual(parse("<t:-1>"), Markup([Timestamp(-1, "f")]))

    def test_large_time(self):
        self.assertEqual(parse("<t:8640000000000>"), Markup([Timestamp(8640000000000, "f")]))

    def test_out_of_range(self):
        self.assertEqual(parse("<t:8640000000001>"), Markup([Text("<t:8640000000001>")]))
