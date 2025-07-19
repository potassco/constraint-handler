from dataclasses import dataclass
from enum import Enum
from clingo.control import Symbol

class DiagnosticType(Enum):
    UNDEFINED_VARIABLE = 1
    CYCLIC_DEPENDENCY = 2

@dataclass
class Diagnostic:
    type: DiagnosticType

@dataclass
class UndefinedVariableDiagnostic(Diagnostic):
    variable: str
    dependent_variable: str

    def __init__(self, variable: str, dependent_variable: str):
        super().__init__(DiagnosticType.UNDEFINED_VARIABLE)
        self.variable = variable
        self.dependent_variable = dependent_variable

    @staticmethod
    def from_symbol(symbol: Symbol):
        return UndefinedVariableDiagnostic(
            variable=str(symbol.arguments[0]),
            dependent_variable=str(symbol.arguments[1])
        )

    def __str__(self):
        return f"Variable '{self.variable}' depends on '{self.dependent_variable}', but '{self.dependent_variable}' is not defined."

@dataclass
class CyclicDependencyDiagnostic(Diagnostic):
    involved_variables: list[str]

    def __init__(self, involved_variables: list[str]):
        super().__init__(DiagnosticType.CYCLIC_DEPENDENCY)
        self.involved_variables = involved_variables

    def __str__(self):
        return f"Cycle detected involving the variables: {', '.join(self.involved_variables)}" 