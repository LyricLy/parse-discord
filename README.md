# parse-discord
A parser for Discord's flavour of text markup that aims to be as accurate as possible.

## Goals
- Parsing message content as returned by Discord's API into a tree
- Matching the behaviour of the desktop client as closely as possible, including edge cases
- Supporting all constructs rendered by the client in plain messages, including emoji, mentions and URLs

## Non-goals
- Parsing markup besides that in message content from the API, like the highlighting seen in the client while typing a message
- Imitating platforms other than web/desktop
- Rendering results to HTML

## Completion
The library is usable in its current state. However, there is work still to be done:
- Supporting emoji sent in text form
    - This refers to doing `parse(":smile:")` instead of `parse("😄")` and getting the same result
    - The Discord client does not produce messages this way and 99.99% of messages from the API will not be in this format
    - However, bots are technically able to produce it, so we should be able to parse it
- More ways to manipulate parse trees
- Guide-level documentation
- Recognizing niche features such as slash command references

## Source
The logic for this module was mostly worked out by hand by testing against Discord's official client through trial and error.
As such, there may be subtle inaccuracies. If you find a case that isn't parsed the same way as it is in Discord, let me know by filing an issue!
