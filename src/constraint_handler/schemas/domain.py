from __future__ import annotations

from collections import namedtuple
from typing import NamedTuple

import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning


class FromFacts(NamedTuple):
    pass


class BoolDomain(NamedTuple):
    pass


class FromList(NamedTuple):
    elements: list[expression.Expr]


type Domain = BoolDomain | FromFacts | FromList


