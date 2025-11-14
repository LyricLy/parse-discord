import unittest
import pathlib
import regex
from ada_url import URL
from hypothesis import given, settings, strategies as st, provisional as pv

from parse_discord import *


# Hypothesis strategies
def link_of(inner):
    return st.builds(Link, pv.urls(), inner, st.text() | st.none(), st.booleans())

def node():
    return st.one_of(
        st.builds(Text, st.text()),
        st.builds(InlineCode, st.text()),
        st.builds(Codeblock, st.text() | st.none(), st.text()),
        link_of(st.none()),
        st.builds(UserMention, st.integers(0)),
        st.builds(ChannelMention, st.integers(0)),
        st.builds(RoleMention, st.integers(0)),
        st.builds(Timestamp, st.integers()),
        st.builds(CustomEmoji, st.integers(0), st.text(), st.booleans()),
        # st.builds(UnicodeEmoji, ???),
        st.just(Everyone()),
        st.just(Here()),
    )

def markup_of(inner):
    return st.builds(Markup, st.lists(inner))

def node_of_markup(markup):
    return st.one_of(
        st.builds(Bold, markup),
        st.builds(Italic, markup),
        st.builds(Underline, markup),
        st.builds(Spoiler, markup),
        st.builds(Strikethrough, markup),
        st.builds(Quote, markup),
        st.builds(Header, markup, st.sampled_from([1, 2, 3])),
        st.builds(Subtext, markup),
        st.builds(List, st.integers(), st.lists(markup)),
    )

def markup():
    return st.recursive(markup_of(node()), lambda m: markup_of(node_of_markup(m)))


class Formatting(unittest.TestCase):
    # parse(s) == parse(str(parse(s))
    def test_weak_round_trip(self):
        cases = []
        for path in pathlib.Path(__file__).parent.glob("*.py"):
            cases.extend(map(eval, regex.findall(r'parse\((r?".*?")\)', path.read_text())))
        for c in cases:
            self.assertEqual(parse(c), parse(str(parse(c))), c)

    # m.normal_form() == parse(str(m)).normal_form()
    @given(markup())
    @settings(deadline=None)
    def test_strong_round_trip(self, markup):
        self.assertEqual(markup.normal_form(), parse(str(markup)))
