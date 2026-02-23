import enum
from typing import Literal

from constraint_handler.schemas.warning import Warning

DEBUG_PRINT = False

DEFAULT_DECISION_LEVEL: Literal[-1] = -1

FALSE_ASSIGNMENTS: Literal["__FALSE_ASSIGNMENTS__"] = "__FALSE_ASSIGNMENTS__"

ENSURE_VAR_NAME: Literal["__ensure__"] = "__ensure__"
EXECUTION_INPUT: Literal["execution_input"] = "execution_input"
EXECUTION_OUTPUT: Literal["execution_output"] = "execution_output"


# enum for value_not_set, assignment_is_false, and value_is_none
class ValueStatus(enum.Enum):
    NOT_SET = "__value_not_set__"
    ASSIGNMENT_IS_FALSE = "__assignment_is_false__"


class EvaluationResult(enum.Enum):
    NOT_CHANGED = "__not_changed__"
    CHANGED = "__changed__"
    CONFLICT = "__conflict__"
    INFER = "__infer__"


class ReasoningMode(enum.Enum):
    STANDARD = "standard"
    BRAVE = "brave"
    CAUTIOUS = "cautious"


class OptimizationStrength(enum.Enum):
    STRICT = "strict"
    LENIENT = "lenient"


REASONING_STAGE_ATOM: Literal["__stage__"] = "__stage__"


REASONING_MODE_PROGRAM = f"""
% Reasoning mode handling
1{{{REASONING_STAGE_ATOM}(1;2;3)}}1.
#heuristic {REASONING_STAGE_ATOM}(1). [990,true]
#heuristic {REASONING_STAGE_ATOM}(2). [989,true]
%#show {REASONING_STAGE_ATOM}/1.
"""


class NoValueSet(Exception):
    pass


type propagator_warning_t = list[Warning]
