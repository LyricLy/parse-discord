import unittest

from parse_discord import *


class Backticks(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(parse("`foo`"), Markup([InlineCode("foo")]))

    def test_empty_inline(self):
        self.assertEqual(parse("``"), Markup([Text("``")]))

    def test_double_inline(self):
        self.assertEqual(parse("``foo``"), Markup([InlineCode("foo")]))

    def test_inline_stability(self):
        self.assertEqual(parse("` `````` `"), Markup([InlineCode(" `````` ")]))

    def test_inline_is_not_escaped(self):
        self.assertEqual(parse("`\`"), Markup([InlineCode("\\")]))
