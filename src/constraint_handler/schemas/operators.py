from __future__ import annotations

from enum import Enum

import constraint_handler.utils.common as common

ComparisonOperator = common.PPEnum("ComparisonOperator", ["eq", "neq", "max", "min"])
StringOperator = common.PPEnum("StringOperator", ["concat", "length"])


class ConditionalOperator(Enum):
    getOrElse = "getOrElse"
    IF = "if"
    ite = "ite"
    hasValue = "hasValue"


ArithmeticOperator = common.PPEnum(
    "ArithmeticOperator",
    [
        "abs",
        "sqrt",
        "cos",
        "sin",
        "tan",
        "acos",
        "asin",
        "atan",
        "minus",
        "floor",
        "ceil",
        "add",
        "sub",
        "mult",
        "int_div",
        "float_div",
        "pow",
        "leq",
        "lt",
        "geq",
        "gt",
        "float_from_int",
        "int_from_float",
    ],
)

LogicOperator = common.PPEnum("LogicOperator", ["conj", "disj", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])

SetOperator = common.PPEnum(
    "SetOperator", ["cardinality", "set_make", "set_isin", "set_notin", "union", "inter", "diff", "subset", "set_fold"]
)

MultimapOperator = common.PPEnum(
    "MultimapOperator",
    [
        "find",
        "find2",
        "multimap_isin",
        "multimap_make",
        "multimap_fold",
        "multimap_fold_i",
        "countKeys",
        "countEntries",
        "sumIntEntries",
        "maxEntries",
        "minEntries",
    ],
)
