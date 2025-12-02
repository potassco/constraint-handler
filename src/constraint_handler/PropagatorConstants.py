import enum

DEBUG_PRINT = False

FALSE_ASSIGNMENTS = "FALSE_ASSIGNMENTS"

ENSURE_VAR_NAME = "__ensure__"

# enum for value_not_set, assignment_is_false, and value_is_none
class ValueStatus(enum.Enum):
    NOT_SET = "value_not_set"
    ASSIGNMENT_IS_FALSE = "assignment_is_false"
