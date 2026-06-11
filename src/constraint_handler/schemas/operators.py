from __future__ import annotations

import constraint_handler.utils.common as common

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
    ],
)

LogicOperator = common.PPEnum("LogicOperator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])

SetOperator = common.PPEnum(
    "SetOperator", ["set_make", "set_isin", "set_notin", "union", "inter", "diff", "subset", "set_fold"]
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
