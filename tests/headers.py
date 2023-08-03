import unittest

from parse_discord import *


class Headers(unittest.TestCase):
    def test_h1(self):
        self.assertEqual(parse("# foo"), Markup([Header1(Markup(["foo"]))]))

    def test_h2(self):
        self.assertEqual(parse("## foo"), Markup([Header2(Markup(["foo"]))]))

    def test_h3(self):
        self.assertEqual(parse("### foo"), Markup([Header3(Markup(["foo"]))]))

    def test_newline_ends(self):
        self.assertEqual(parse("# foo\ning"), Markup([Header1(Markup(["foo"])), Text("ing")]))

    def test_ender_trick(self):
        self.assertEqual(parse("*# foo*ing"), Markup([Bold(Markup([Header1(Markup(["foo"]))])), Text("ing")]))

    def test_only_at_start(self):
        self.assertEqual(parse("a # foo"), Markup([Text("a # foo")]))

    def test_indentation_breaks(self):
        self.assertEqual(parse(" # foo"), Markup([Text(" # foo")]))
