import unittest

from parse_discord import *


class Mentions(unittest.TestCase):
    def test_user(self):
        self.assertEqual(parse("<@0>"), Markup([UserMention(0)]))

    def test_user_exclam(self):
        self.assertEqual(parse(r"<@!0>"), Markup([UserMention(0)]))

    def test_role(self):
        self.assertEqual(parse(r"<@&0>"), Markup([RoleMention(0)]))

    def test_channel(self):
        self.assertEqual(parse("<#0>"), Markup([ChannelMention(0)]))

    def test_everyone(self):
        self.assertEqual(parse("@everyone"), Markup([Everyone()]))

    def test_here(self):
        self.assertEqual(parse("@here"), Markup([Here()]))

    def test_user_escape(self):
        self.assertEqual(parse(r"\<@319753218592866315>"), Markup([Text("<@319753218592866315>")]))

    def test_everyone_escape(self):
        self.assertEqual(parse(r"\@everyone"), Markup([Text("@everyone")]))
