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
