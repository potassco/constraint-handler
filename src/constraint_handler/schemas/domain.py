from __future__ import annotations

from typing import NamedTuple

import constraint_handler.schemas.expression as expression


class Definition(NamedTuple):
    pass


class FromFacts(NamedTuple):
    pass


class BoolDomain(NamedTuple):
    pass


class FromList(NamedTuple):
    elements: list[expression.Expr]


class Set(NamedTuple):
    pass


class Multimap(NamedTuple):
    pass


type Domain = Definition | BoolDomain | FromFacts | FromList | Set | Multimap
