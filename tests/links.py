import unittest

from urlstd.parse import URL

from parse_discord import *


def u(url):
    return Link(URL(url), None, None, False)

class Links(unittest.TestCase):
    def test_bare(self):
        self.assertEqual(parse("https://example.com"), Markup([u("https://example.com")]))

    def test_not_single_char(self):
        self.assertEqual(parse("http://a"), Markup([Text("http://a")]))
        self.assertEqual(parse("http://a."), Markup([Text("http://a.")]))
        self.assertEqual(parse("http://a)"), Markup([u("http://a"), Text(")")]))

    def test_no_ending_special(self):
        self.assertEqual(parse("http://ab."), Markup([u("http://ab"), Text(".")]))

    def test_no_ending_unmatched_close_paren(self):
        self.assertEqual(parse("https://ab)"), Markup([u("https://ab"), Text(")")]))
        self.assertEqual(parse("https://a))"), Markup([u("https://a)"), Text(")")]))
        self.assertEqual(parse("https://(a)"), Markup([u("https://(a)")]))
        self.assertEqual(parse("https://(a))"), Markup([u("https://(a)"), Text(")")]))
        # yes, this is correct! close parens are only counted at the end
        self.assertEqual(parse("https://(a)b)"), Markup([u("https://(a)b)")]))
        self.assertEqual(parse("https://a)."), Markup([u("https://a"), Text(").")]))
        self.assertEqual(parse("https://a.)"), Markup([u("https://a."), Text(")")]))

    def test_steam(self):
        self.assertEqual(parse("steam://*a*"), Markup([Text("steam://*a*")]))
