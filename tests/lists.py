import unittest

from parse_discord import *


class Lists(unittest.TestCase):
    def test_asterisk_ul(self):
        self.assertEqual(parse("* foo"), Markup([List([Markup([Text("foo")])], None)]))

    def test_hyphen_ul(self):
        self.assertEqual(parse("- foo"), Markup([List([Markup([Text("foo")])], None)]))

    def test_ol(self):
        self.assertEqual(parse("1. foo"), Markup([List([Markup([Text("foo")])], 1)]))

    def test_ol_bounds(self):
        self.assertEqual(parse("0. foo"), Markup([List([Markup([Text("foo")])], 1)]))
        self.assertEqual(parse("1000000001. foo"), Markup([List([Markup([Text("foo")])], 1000000000)]))

    def test_indent(self):
        self.assertEqual(parse("- a\n b"), Markup([List([Markup([Text("a")])], None), Text("b")]))
        self.assertEqual(parse("- a\n   b"), Markup([List([Markup([Text("a\n b")])], None)]))
        self.assertEqual(parse("1. a\n   b"), Markup([List([Markup([Text("a\nb")])], 1)]))
        self.assertEqual(parse("1. a\n    b"), Markup([List([Markup([Text("a\n b")])], 1)]))
        self.assertEqual(parse("1.  a\n    b"), Markup([List([Markup([Text("a\nb")])], 1)]))

    def test_null_grab(self):
        self.assertEqual(parse("* \na"), Markup([List([Markup([Text("\na")])], None)]))

    def test_anti_grab(self):
        self.assertEqual(parse("* \n* b"), Markup([List([Markup([]), Markup([Text("b")])], None)]))

    def test_nesting(self):
        self.assertEqual(
            parse("1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. a"),
            Markup([
                List([Markup([
                    List([Markup([
                        List([Markup([
                            List([Markup([
                                List([Markup([
                                    List([Markup([
                                        List([Markup([
                                            List([Markup([
                                                List([Markup([
                                                    List([Markup([
                                                        List([Markup([
                                                            Text("1. a"),
                                                        ])], 1)
                                                    ])], 1)
                                                ])], 1)
                                            ])], 1)
                                        ])], 1)
                                    ])], 1)
                                ])], 1)
                            ])], 1)
                        ])], 1)
                    ])], 1)
                ])], 1)
            ])
        )

    def test_multi(self):
        self.assertEqual(parse("0. a\n0. b"), Markup([List([Markup([Text("a")]), Markup([Text("b")])], 1)]))

    def test_reverse_indent(self):
        self.assertEqual(
            parse("   1. a\n  2. b\n 3. c\n4. d"),
            Markup([
                Text("   "),
                List([
                    Markup([
                        Text("a\n"),
                        List([
                            Markup([Text("b")]), 
                        ], 2),
                    ]),
                    Markup([Text("c")]),
                    Markup([Text("d")]),
                ], 1),
            ]),
        )

    def test_random_example(self):
        self.assertEqual(
            parse("* a\n    b\n    1. c\n    2. d\n    c"),
            Markup([
                List([Markup([
                    Text("a\n  b\n  "),
                    List([Markup([
                        Text("c\n"),
                        List([Markup([Text("d")])], 2),
                        Text("c"),
                    ])], 1),
                ])], None),
            ]),
        )

    def test_quotes_work(self):
        self.assertEqual(parse("- > a"), Markup([List([Markup([Quote(Markup([Text("a")]))])], None)]))

    def test_headers_do_not(self):
        self.assertEqual(parse("- # a"), Markup([List([Markup([Text("# a")])], None)]))

    def test_quotes_work_nested(self):
        self.assertEqual(
            parse("1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. > a"),
            Markup([
                List([Markup([
                    List([Markup([
                        List([Markup([
                            List([Markup([
                                List([Markup([
                                    List([Markup([
                                        List([Markup([
                                            List([Markup([
                                                List([Markup([
                                                    List([Markup([
                                                        List([Markup([
                                                            Quote(Markup([
                                                                Text("a"),
                                                            ]))
                                                        ])], 1)
                                                    ])], 1)
                                                ])], 1)
                                            ])], 1)
                                        ])], 1)
                                    ])], 1)
                                ])], 1)
                            ])], 1)
                        ])], 1)
                    ])], 1)
                ])], 1)
            ])
        )

    def test_list_in_quote(self):
        self.assertEqual(parse("> - a"), Markup([Quote(Markup([List([Markup([Text("a")])], None)]))]))

    def test_strip_passthrough(self):
        self.assertEqual(parse("- a\N{IDEOGRAPHIC SPACE} \n"), Markup([List([Markup([Text("a\N{IDEOGRAPHIC SPACE}")])], None)]))
