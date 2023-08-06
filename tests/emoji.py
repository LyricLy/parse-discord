import unittest

from parse_discord import *


class Emoji(unittest.TestCase):
    def test_unicode(self):
        self.assertEqual(parse("🥺"), Markup([UnicodeEmoji("🥺")]))

    def test_unicode_escape(self):
        self.assertEqual(parse("\🥺"), Markup([Text("🥺")]))

    def test_custom(self):
        self.assertEqual(parse("<:name:0>"), Markup([CustomEmoji(0, "name", False)]))

    def test_custom_animated(self):
        self.assertEqual(parse("<a:name:0>"), Markup([CustomEmoji(0, "name", True)]))

    def test_reject_bad_name(self):
        self.assertEqual(parse("<:-:0>"), Markup([Text("<:-:0>")]))
