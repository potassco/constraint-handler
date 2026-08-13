from __future__ import annotations

from typing import NamedTuple


class Definition(NamedTuple):
    pass


class FromFacts(NamedTuple):
    pass


class BoolDomain(NamedTuple):
    pass


class Open(NamedTuple):
    pass


class Set(NamedTuple):
    pass


class Multimap(NamedTuple):
    pass


type Domain = Definition | BoolDomain | FromFacts | Open | Set | Multimap
