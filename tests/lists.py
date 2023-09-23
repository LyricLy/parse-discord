import unittest

from parse_discord import *


class Lists(unittest.TestCase):
    def test_asterisk_ul(self):
        self.assertEqual(parse("* foo"), Markup([List(None, [Markup([Text("foo")])])]))

    def test_hyphen_ul(self):
        self.assertEqual(parse("- foo"), Markup([List(None, [Markup([Text("foo")])])]))

    def test_ol(self):
        self.assertEqual(parse("1. foo"), Markup([List(1, [Markup([Text("foo")])])]))

    def test_ol_bounds(self):
        self.assertEqual(parse("0. foo"), Markup([List(1, [Markup([Text("foo")])])]))
        self.assertEqual(parse("1000000001. foo"), Markup([List(1000000000, [Markup([Text("foo")])])]))

    def test_indent(self):
        self.assertEqual(parse("- a\n b"), Markup([List(None, [Markup([Text("a\nb")])])]))
        self.assertEqual(parse("- a\n   b"), Markup([List(None, [Markup([Text("a\n b")])])]))
        self.assertEqual(parse("1. a\n   b"), Markup([List(1, [Markup([Text("a\nb")])])]))
        self.assertEqual(parse("1. a\n    b"), Markup([List(1, [Markup([Text("a\n b")])])]))
        self.assertEqual(parse("1.  a\n    b"), Markup([List(1, [Markup([Text("a\nb")])])]))

    def test_null_grab(self):
        self.assertEqual(parse("* \na"), Markup([List(None, [Markup([Text("\na")])])]))

    def test_nesting(self):
        self.assertEqual(
            parse("1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. a"),
            Markup([
                List(1, [Markup([
                    List(1, [Markup([
                        List(1, [Markup([
                            List(1, [Markup([
                                List(1, [Markup([
                                    List(1, [Markup([
                                        List(1, [Markup([
                                            List(1, [Markup([
                                                List(1, [Markup([
                                                    List(1, [Markup([
                                                        List(1, [Markup([
                                                            Text("1. a"),
                                                        ])])
                                                    ])])
                                                ])])
                                            ])])
                                        ])])
                                    ])])
                                ])])
                            ])])
                        ])])
                    ])])
                ])])
            ])
        )

    def test_multi(self):
        self.assertEqual(parse("0. a\n0. b"), Markup([List(1, [Markup([Text("a")]), Markup([Text("b")])])]))

    def test_reverse_indent(self):
        self.assertEqual(
            parse("   1. a\n  2. b\n 3. c\n4. d"),
            Markup([
                Text("   "),
                List(1, [
                    Markup([
                        Text("a\n"),
                        List(2, [
                            Markup([Text("b")]), 
                            Markup([Text("c")]),
                        ]),
                    ]),
                    Markup([Text("d")]),
                ]),
            ]),
        )

    def test_random_example(self):
        self.assertEqual(
            parse("* a\n    b\n    1. c\n    2. d\n    c"),
            Markup([
                List(None, [Markup([
                    Text("a\n  b\n  "),
                    List(1, [Markup([
                        Text("c\n"),
                        List(2, [Markup([Text("d")])]),
                        Text("c"),
                    ])]),
                ])]),
            ]),
        )

    def test_quotes_work(self):
        self.assertEqual(parse("- > a"), Markup([List(None, [Markup([Quote(Markup([Text("a")]))])])]))

    def test_headers_do_not(self):
        self.assertEqual(parse("- # a"), Markup([List(None, [Markup([Text("# a")])])]))
