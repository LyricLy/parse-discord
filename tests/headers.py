import unittest

from parse_discord import *


class Headers(unittest.TestCase):
    def test_h1(self):
        self.assertEqual(parse("# foo"), Markup([Header(Markup([Text("foo")]), 1)]))

    def test_h2(self):
        self.assertEqual(parse("## foo"), Markup([Header(Markup([Text("foo")]), 2)]))

    def test_h3(self):
        self.assertEqual(parse("### foo"), Markup([Header(Markup([Text("foo")]), 3)]))

    def test_newline_ends(self):
        self.assertEqual(parse("# foo\ning"), Markup([Header(Markup([Text("foo")]), 1), Text("ing")]))

    def test_ender_trick(self):
        self.assertEqual(parse("*# foo*ing"), Markup([Italic(Markup([Header(Markup([Text("foo")]), 1)])), Text("ing")]))

    def test_only_at_start(self):
        self.assertEqual(parse("a # foo"), Markup([Text("a # foo")]))

    def test_indentation_breaks(self):
        self.assertEqual(parse(" # foo"), Markup([Text(" # foo")]))

    def test_even_through_asterisks(self):
        self.assertEqual(parse(" *# foo*"), Markup([Text(" "), Italic(Markup([Text("# foo")]))]))

    def test_leading_hash(self):
        self.assertEqual(parse("# # a"), Markup([Text("# # a")]))

    def test_strips(self):
        self.assertEqual(parse("#    a #   ####   "), Markup([Header(Markup([Text("a #")]), 1)]))

    def test_newline_start(self):
        self.assertEqual(parse("#\na"), Markup([Header(Markup([Text("a")]), 1)]))
