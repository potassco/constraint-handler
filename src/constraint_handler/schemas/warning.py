from __future__ import annotations

import typing

# import constraint_handler.schemas.expression as expression
import constraint_handler.utils.common as common


class Error(typing.NamedTuple):
    kind: Kind
    message: typing.Any


ExpressionWarning = common.PPEnum(
    "ExpressionWarning", ["notImplemented", "pythonError", "syntaxError", "zeroDivisionError"]
)


class Expression(typing.NamedTuple):
    symbol: ExpressionWarning


class OtherError(typing.NamedTuple):
    pass


PreferenceWarning = common.PPEnum("PreferenceWarning", ["unsupported"])


class Preference(typing.NamedTuple):
    symbol: PreferenceWarning


class Propagator(typing.NamedTuple):
    pass


StatementWarning = common.PPEnum("StatementWarning", ["notImplemented", "evaluatorError", "pythonError"])


class Statement(typing.NamedTuple):
    symbol: StatementWarning


# TODO: rename failed_operation to failedOperation
TypeWarning = common.PPEnum("TypeWarning", ["failed_operation"])


class Type(typing.NamedTuple):
    symbol: TypeWarning


VariableWarning = common.PPEnum(
    "VariableWarning",
    ["badValue", "emptyDomain", "multipleDeclarations", "multipleDefinitions", "undeclared", "confusingName"],
)


class Variable(typing.NamedTuple):
    symbol: VariableWarning


type Kind = Expression | OtherError | Preference | Propagator | Statement | Type | Variable


class Warning(typing.NamedTuple):
    id: Kind
    declarations: tuple[typing.Any, ...]  # expression.constant
    info: typing.Any


class Forbid_warning(typing.NamedTuple):
    label: typing.Any  # expression.constant
    symbol: Kind
