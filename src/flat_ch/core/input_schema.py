from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from flat_ch.core.domain import FlatFact, UserInput


class LayoutToken(Enum):
    """
    Tokens representing expected argument types in the input schema layout.
    """

    IDENTIFIER = auto()
    """
    An identifier token.

    This token is used for unique names of variables and sets. For this reason it usually
    involves collision checks to prevent redefinition or redeclaration of variables and sets.
    """

    EXPRESSION = auto()
    """ An expression term that needs to be flattened. """

    PASS = auto()
    """ An argument that should be passed through directly without processing. """


@dataclass(frozen=True)
class InputSchema:
    """
    Defines the expected structure of a top-level declaration.
    """

    flat_fact: FlatFact
    """ The FlatFact to emit for this declaration. """

    layout: Tuple[LayoutToken, ...]
    """ The expected sequence of tokens in the declaration's arguments."""

    collision_state: Optional[str] = None
    """ If set, this declaration will trigger a collision check."""


STATEMENT_SCHEMAS = {
    UserInput.DECLARE: InputSchema(
        flat_fact=FlatFact.VARIABLE_DECLARE, layout=(LayoutToken.IDENTIFIER,), collision_state="declared"
    ),
    UserInput.SET_DECLARE: InputSchema(
        flat_fact=FlatFact.SET, layout=(LayoutToken.IDENTIFIER,), collision_state="set_declared"
    ),
    UserInput.DEFINE: InputSchema(
        flat_fact=FlatFact.VARIABLE_DEFINE,
        layout=(LayoutToken.IDENTIFIER, LayoutToken.EXPRESSION),
        collision_state="defined",
    ),
    UserInput.DOMAIN: InputSchema(
        flat_fact=FlatFact.VARIABLE_DOMAIN,
        layout=(LayoutToken.IDENTIFIER, LayoutToken.EXPRESSION),
        collision_state="declared",
    ),
    UserInput.ENSURE: InputSchema(flat_fact=FlatFact.ENSURE, layout=(LayoutToken.IDENTIFIER, LayoutToken.EXPRESSION)),
    UserInput.BOOL_EVALUATE: InputSchema(
        flat_fact=FlatFact.BOOL_EVALUATE, layout=(LayoutToken.PASS, LayoutToken.EXPRESSION)
    ),
    UserInput.SET_BASE_DOMAIN: InputSchema(
        flat_fact=FlatFact.SET_BASE_DOMAIN, layout=(LayoutToken.IDENTIFIER, LayoutToken.EXPRESSION)
    ),
    UserInput.SET_ASSIGN: InputSchema(
        flat_fact=FlatFact.SET_ASSIGN, layout=(LayoutToken.IDENTIFIER, LayoutToken.EXPRESSION)
    ),
    UserInput.OPTIMIZE_SUM: InputSchema(
        flat_fact=FlatFact.OPTIMIZE_SUM,
        layout=[LayoutToken.EXPRESSION, LayoutToken.PASS, LayoutToken.PASS],
        collision_state=None,
    ),
    UserInput.OPTIMIZE_PRECISION: InputSchema(
        flat_fact=FlatFact.OPTIMIZE_PRECISION,
        layout=(
            LayoutToken.EXPRESSION,
            LayoutToken.PASS,
        ),
        collision_state=None,
    ),
}
