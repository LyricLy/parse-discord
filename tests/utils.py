from parse_discord.ast import Style

def depth_of_insanity(m):
    if not isinstance(m, Style):
        return 0
    return 1 + depth_of_insanity(m.inner.nodes[0])
