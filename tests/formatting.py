import unittest
import pathlib
import regex

from parse_discord import *


class Formatting(unittest.TestCase):
    def test_round_trip(self):
        cases = []
        for path in pathlib.Path(__file__).parent.glob("*.py"):
            cases.extend(map(eval, regex.findall(r'parse\((r?".*?")\)', path.read_text())))
        for c in cases:
            self.assertEqual(parse(c), parse(str(parse(c))), c)
