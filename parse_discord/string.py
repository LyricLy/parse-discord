"""Internal Discord string operations. Not exported."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from urlstd.parse import URL


def url_to_text(url: URL) -> str:
    """Discord's custom function from a WHATWG URL to a string."""
    if url.origin ==  "null" and url.pathname.startswith("//"):
        s = url.protocol
    else:
        t = "".join([url.username, *[":", url.password]*bool(url.password), "@"]*bool(url.username))
        s = f"{url.protocol}//{t}{url.host}"
    return f"{s}{url.pathname}{url.search}{url.hash}"
