import unittest

from parse_discord import *


class Quotes(unittest.TestCase):
    def test_line_quote(self):
        self.assertEqual(parse("> foo"), Markup([Quote(Markup([Text("foo")]))]))

    def test_line_quotes(self):
        self.assertEqual(parse("> foo\n> bar"), Markup([Quote(Markup([Text("foo\nbar")]))]))

    def test_block_quote(self):
        self.assertEqual(parse(">>> foo\nbar"), Markup([Quote(Markup([Text("foo\nbar")]))]))

    def test_does_not_strip(self):
        self.assertEqual(parse(">  foo"), Markup([Quote(Markup([Text(" foo")]))]))

    def test_not_in_middle(self):
        self.assertEqual(parse("a > foo"), Markup([Text("a > foo")]))

    def test_goes_through(self):
        self.assertEqual(parse("a *> foo*"), Markup([Text("a "), Italic(Markup([Text("> foo")]))]))

    def test_leading_space_ok(self):
        self.assertEqual(parse(" > foo"), Markup([Text(" "), Quote(Markup([Text("foo")]))]))

    def test_no_nesting(self):
        self.assertEqual(parse("> > foo\n> > bar"), Markup([Quote(Markup([Text("> foo\n> bar")]))]))

    def test_early_close(self):
        self.assertEqual(parse("__>>> a\nb__c"), Markup([Underline(Markup([Quote(Markup([Text("a\nb")]))])), Text("c")]))

    def test_codeblock_scourge(self):
        self.assertEqual(parse("*> ```\nfoo```*"), Markup([Italic(Markup([Quote(Markup([Text("```")])), Text("foo```")]))]))

    def test_empty(self):
        self.assertEqual(parse("> "), Markup([Quote(Markup([]))]))

    def test_strip_trailing(self):
        self.assertEqual(parse("> foo  \nbar"), Markup([Quote(Markup([Text("foo")])), Text("bar")]))
