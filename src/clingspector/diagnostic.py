from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from clingo.control import Symbol

from clingspector.utils.asp import asp_to_python_list

class DiagnosticType(Enum):
    UNDEFINED_VARIABLE = "cs_undefined_variable"
    CYCLIC_DEPENDENCY = "cs_cyclic_dependency"
    UNSUPPORTED_OPERATOR =  "cs_unsupported_operator"
    UNSUPPORTED_ARGUMENT_TYPE = "cs_unsupported_argument_type"
    UNSUPPORTED_TYPE = "cs_unsupported_type"

@dataclass
class Diagnostic:

    @staticmethod
    def from_symbol(symbol: Symbol) -> Optional[Diagnostic]:
        """Create a diagnostic from a Clingo symbol."""
        try:
            diag_type = DiagnosticType(symbol.name)
        except ValueError:
            return None

        diagnostic_class = Diagnostic._registry.get(diag_type)
        if diagnostic_class and hasattr(diagnostic_class, "from_symbol"):
            return diagnostic_class.from_symbol(symbol)
        return None

@dataclass
class UndefinedVariableDiagnostic(Diagnostic):
    variable: str
    undefined_variable: str

    @staticmethod
    def from_symbol(symbol: Symbol):
        return UndefinedVariableDiagnostic(
            variable=str(symbol.arguments[0]),
            undefined_variable=str(symbol.arguments[1])
        )

    def __str__(self):
        return f"Variable '{self.variable}' depends on '{self.undefined_variable}', but '{self.undefined_variable}' is not defined."

@dataclass
class CyclicDependencyDiagnostic(Diagnostic):
    involved_variables: list[str]

    @staticmethod
    def from_symbol(symbol: Symbol):
        involved_symbols = asp_to_python_list(symbol.arguments[1])
        involved_symbols.reverse()

        return CyclicDependencyDiagnostic(
            involved_variables=[s.name for s in involved_symbols]
        )

    def __str__(self):
        return f"Cycle detected involving the variables: [{', '.join(self.involved_variables)}]" 
    
@dataclass
class UnsupportedOperatorDiagnostic(Diagnostic):
    operator: str

    @staticmethod
    def from_symbol(symbol: Symbol):
        return UnsupportedOperatorDiagnostic(operator=str(symbol.arguments[0]))

    def __str__(self):
        return f"Unsupported operator: {self.operator}"


@dataclass
class UnsupportedArgumentTypeDiagnostic(Diagnostic):
    operator: str
    arguments: list[str]

    @staticmethod
    def from_symbol(symbol: Symbol):
        return UnsupportedArgumentTypeDiagnostic(
            operator=str(symbol.arguments[0]),
            arguments=[arg.name for arg in symbol.arguments[1].arguments]
        )

    def __str__(self):
        return f"Unsupported argument types for ({self.operator}): [{", ".join(self.arguments)}]"
    

def register_diagnostics(cls):
    """ Decorator to attach _registry to Diagnostic after subclasses are defined.
    
        The registry is a mapping from DiagnosticType to the corresponding Diagnostic subclass
        and is used to create instances of diagnostics based on Clingo symbols.
    """
    cls._registry = {
        DiagnosticType.UNDEFINED_VARIABLE: UndefinedVariableDiagnostic,
        DiagnosticType.CYCLIC_DEPENDENCY: CyclicDependencyDiagnostic,
        DiagnosticType.UNSUPPORTED_OPERATOR: UnsupportedOperatorDiagnostic,
        DiagnosticType.UNSUPPORTED_ARGUMENT_TYPE: UnsupportedArgumentTypeDiagnostic
    }
    return cls

Diagnostic = register_diagnostics(Diagnostic)