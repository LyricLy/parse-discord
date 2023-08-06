# parse-discord
A parser for Discord's flavour of text markup that aims to be as accurate as possible.

## Goals
- Parsing message content as returned by Discord's API into a tree
- Matching the behaviour of the desktop client as closely as possible, including edge cases
- Supporting all constructs rendered by the client in plain messages, including emoji, mentions and URLs

## Non-goals
- Parsing markup besides that in message content from the API, like the highlighting seen in the client while typing a message
- Imitating platforms other than web/desktop
- Robustly rendering results to HTML (though methods to do this are still included)

## Source
The logic for this module was mostly worked out by hand by testing against Discord's official client through trial and error.
Some features have been checked against the client's source code, but ther may be subtle inaccuracies. If you find a case that
isn't parsed the same as it is in Discord, let me know by filing an issue!
