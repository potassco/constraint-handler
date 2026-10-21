from enum import Enum


class UserInput(str, Enum):
    """The top-level elements that the CH API can declare."""

    DEFINE = "variable_define"
    DECLARE = "variable_declare"
    DOMAIN = "variable_domain"
    DEFAULT = "variable_default"
    VALUE = "val"
    VARIABLE = "variable"
    OPERATION = "operation"
    ENSURE = "ensure"
    CHECK = "check"
    EVALUATE = "evaluate"
    BOOL_EVALUATE = "bool_evaluate"
    SET_DECLARE = "set_declare"
    SET_BASE_DOMAIN = "set_baseDomain"
    SET_ASSIGN = "set_assign"
    OPTIMIZE_SUM = "optimize_maximizeSum"
    OPTIMIZE_PRECISION = "optimize_precision"
    EXECUTION_DECLARE = "execution_declare"
    STATEMENT_SEQUENCE = "seq2"
    STATEMENT_ASSIGN = "assign"
    STATEMENT_ASSERT = "assert"
    STATEMENT_IF = "if"
    STATEMENT_NOOP = "noop"
    STATEMENT_PYTHON = "statement_python"
