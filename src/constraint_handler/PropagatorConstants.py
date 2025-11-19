import enum
from dataclasses import dataclass

DEBUG_PRINT = False

FALSE_ASSIGNMENTS = "FALSE_ASSIGNMENTS"


# enum for value_not_set, assignment_is_false, and value_is_none
class ValueStatus(enum.Enum):
    NOT_SET = "value_not_set"
    ASSIGNMENT_IS_FALSE = "assignment_is_false"


@dataclass
class AtomNames:
    ASSIGN: str = "propagator_assign"
    ENSURE: str = "propagator_ensure"
    EVALUATE: str = "evaluate"
    SET_DECLARE: str = "propagator_set_declare"
    SET_ASSIGN: str = "propagator_set_assign"
    MULTIMAP_DECLARE: str = "propagator_multimap_declare"
    MULTIMAP_ASSIGN: str = "propagator_multimap_assign"
    SOLVER_ID: str = "_main_solverIdentifier"
    OPTIMIZE_SUM: str = "propagator_optimize_maximizeSum"
