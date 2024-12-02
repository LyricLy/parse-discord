import unittest

from parse_discord import *


class Backticks(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(parse("`foo`"), Markup([InlineCode("foo")]))

    def test_empty_inline(self):
        self.assertEqual(parse("``"), Markup([Text("``")]))

    def test_just_space(self):
        self.assertEqual(parse("` `"), Markup([InlineCode(" ")]))

    def test_double_inline(self):
        self.assertEqual(parse("``foo``"), Markup([InlineCode("foo")]))

    def test_inline_stability(self):
        self.assertEqual(parse("```` `"), Markup([InlineCode("```")]))

    def test_strips(self):
        self.assertEqual(parse("``  `a  ``"), Markup([InlineCode(" `a  ")]))
                                  ##  ##                             ##
    def test_inline_is_not_escaped(self):
        self.assertEqual(parse(r"`\`"), Markup([InlineCode("\\")]))

    def test_block(self):
        self.assertEqual(parse("```foo```"), Markup([Codeblock(None, "foo")]))

    def test_block_strip(self):
        self.assertEqual(parse("```\nfoo \n```"), Markup([Codeblock(None, "foo ")]))

    def test_block_lang(self):
        self.assertEqual(parse("```py\nfoo```"), Markup([Codeblock("py", "foo")]))

    def test_false_lang(self):
        self.assertEqual(parse("```py\n\n```"), Markup([Codeblock(None, "py")]))

    def test_one_tick_block(self):
        self.assertEqual(parse("```````"), Markup([Codeblock(None, "`")]))

    def test_block_that_could_be_inline(self):
        self.assertEqual(parse("```\n``\n```"), Markup([Codeblock(None, "``")]))

    def test_block_that_could_be_different(self):
        self.assertEqual(parse("```\n```\n```"), Markup([Codeblock(None, "```")]))

    def test_false_block(self):
        self.assertEqual(parse("```\n```"), Markup([InlineCode("\n")]))

    def test_two_together_inline(self):
        self.assertEqual(parse("`a` b `c`"), Markup([InlineCode("a"), Text(" b "), InlineCode("c")]))

    def test_two_together_block(self):
        self.assertEqual(parse("```a``` b ```c```"), Markup([Codeblock(None, "a"), Text(" b "), Codeblock(None, "c")]))
