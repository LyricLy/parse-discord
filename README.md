# parse-discord
A parser for Discord's flavour of text markup that aims to be as accurate as possible.

## Goals
- Parsing message content as returned by Discord's API into a tree
- Matching the behaviour of the desktop client as closely as possible, including edge cases
- Supporting all constructs in plain message content, including emoji and mentions

## Non-goals
- Parsing markup besides that in message content from the API, like the URL syntax supported in embeds or the highlighting seen in the client while typing a message
- Imitating platforms other than web/desktop
- Robustly rendering results to HTML (though methods to do this are still included)
