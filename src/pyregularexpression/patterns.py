"""Common regular‑expression patterns.

Add your own `Pattern` subclasses or raw pattern strings here.
"""

import re
from dataclasses import dataclass
from typing import Pattern as RePattern

@dataclass(frozen=True)
class Pattern:
    raw: str

    def compile(self, flags: int = 0) -> RePattern[str]:
        return re.compile(self.raw, flags)

    def match(self, string: str, flags: int = 0):
        return self.compile(flags).match(string)

    def search(self, string: str, flags: int = 0):
        return self.compile(flags).search(string)

    def fullmatch(self, string: str, flags: int = 0):
        return self.compile(flags).fullmatch(string)


# Example patterns ---------------------------------------------------------

EMAIL = Pattern(
    raw=r"""(?ix)           # case‑insensitive, verbose
    ^
    [a-z0-9._%+-]+            # local part
    @
    [a-z0-9.-]+\.            # domain name prefix
    [a-z]{2,63}               # TLD
    $
    """
)

URI = Pattern(
    raw=r"""(?i)
    \b
    (?:https?|ftp)://
    [^\s/$.?#].[^\s]*
    \b
    """
)
