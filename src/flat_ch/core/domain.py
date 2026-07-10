from enum import Enum

class UserInput(str, Enum):
    """
    The top-level elements that the user can declare in their ASP input.
    """
    ALIAS = "variable_from_scope"
    DEFINE = "variable_define"
    DECLARE = "variable_declare"
    DOMAIN = "variable_domain"
    VALUE = "val"
    VARIABLE = "variable"
    OPERATION = "operation"
    ENSURE = "ensure"
    BOOL_EVALUATE = "bool_evaluate"
    SET_DECLARE = "set_declare"
    SET_BASE_DOMAIN = "set_baseDomain"
    SET_ASSIGN = "set_assign"
    BIND = "bind"
    OPTIMIZE_SUM = "optimize_maximizeSum"
    OPTIMIZE_PRECISION = "optimize_precision"
    PAIR = "pair"

class FlatFact(str, Enum):
    """
    The different types of facts that can be emitted by the flattener.
    """
    EXPRESSION_VALUE = "expr_val"
    EXPRESSION_VARIABLE = "expr_var"
    VARIABLE_DEFINE = "var_def"
    VARIABLE_DECLARE = "var_decl"
    VARIABLE_DOMAIN = "var_dom"
    ENSURE = "ensure"
    EVALUATE = "evaluate"
    BOOL_EVALUATE = "bool_evaluate"
    SET = "set_decl"
    SET_BASE_DOMAIN = "set_base_domain"
    SET_ASSIGN = "set_assign"
    OPTIMIZE_SUM = "optimize_sum"
    OPTIMIZE_PRECISION = "optimize_precision"
    PAIR = "pair"

    @property
    def variables(self) -> tuple[str, ...]:
        """Defines the exact positional argument names for the schema projection."""
        mapping = {
            FlatFact.VARIABLE_DECLARE: ("NAME",),
            FlatFact.VARIABLE_DOMAIN:  ("NAME", "EXPR_ID"),
            FlatFact.VARIABLE_DEFINE:  ("NAME", "EXPR_ID"),
            FlatFact.EXPRESSION_VALUE: ("ID", "TYPE_ID", "VALUE"),
            FlatFact.EXPRESSION_VARIABLE: ("ID", "NAME"),
            FlatFact.ENSURE:           ("NAME", "EXPR_ID"),
            FlatFact.EVALUATE:         ("OP", "ARGS", "EXPR_ID"),
            FlatFact.BOOL_EVALUATE:    ("EXPR", "EXPR_ID"),
            FlatFact.SET:              ("NAME",),
            FlatFact.SET_BASE_DOMAIN:  ("NAME", "EXPR_ID"),
            FlatFact.SET_ASSIGN:       ("NAME", "EXPR_ID"),
            FlatFact.PAIR:             ("ID", "KEY_EXPR_ID", "VALUE_EXPR_ID"),
            FlatFact.OPTIMIZE_SUM:     ("ID", "ELEM", "PRIO"),
            FlatFact.OPTIMIZE_PRECISION: ("EXPR_ID", "PRIO"),
        }
        return mapping.get(self, ("ID",))