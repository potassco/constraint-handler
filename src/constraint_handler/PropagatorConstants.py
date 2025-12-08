import enum

DEBUG_PRINT = False

FALSE_ASSIGNMENTS = "__FALSE_ASSIGNMENTS__"

ENSURE_VAR_NAME = "__ensure__"
EXECUTION_INPUT = "execution_input"
EXECUTION_OUTPUT = "execution_output"


# enum for value_not_set, assignment_is_false, and value_is_none
class ValueStatus(enum.Enum):
    NOT_SET = "__value_not_set__"
    ASSIGNMENT_IS_FALSE = "__assignment_is_false__"


class EvaluationResult(enum.Enum):
    NOT_CHANGED = "__not_changed__"
    CHANGED = "__changed__"
    CONFLICT = "__conflict__"
    INFER = "__infer__"
