""" Diagnostic classes for Clingspector."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from clingo.control import Symbol

from clingspector.utils.asp import asp_to_python_list


class DiagnosticType(Enum):
    """Diagnostic types for Clingspector."""

    UNDEFINED_VARIABLE = "cs_undefined_variable"
    CYCLIC_DEPENDENCY = "cs_cyclic_dependency"
    UNSUPPORTED_OPERATOR_TYPE = "cs_unsupported_operator_type"
    UNSUPPORTED_ARGUMENT_TYPE = "cs_unsupported_argument_type"
    UNSUPPORTED_TYPE = "cs_unsupported_type"


@dataclass
class Diagnostic:
    """Base class for diagnostics.

    This also uses the attribute `_registry` to call the
    `from_symbol` method of the correct diagnostic class.

    The attribute `_registry` is populated by the `register_diagnostics`
    decorator at the end of this file.
    """

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
    """Diagnostic for undefined variables."""

    variable: str
    """ The variable depending on some other, undefined, variable."""

    undefined_variable: str
    """ The variable that is not defined."""

    @staticmethod
    def from_symbol(symbol: Symbol):
        """Create an UndefinedVariableDiagnostic from a Clingo symbol."""

        return UndefinedVariableDiagnostic(
            variable=str(symbol.arguments[0]), undefined_variable=str(symbol.arguments[1])
        )

    def __str__(self):
        return (
            f"Variable '{self.variable}' depends on '{self.undefined_variable}', "
            f"but '{self.undefined_variable}' is not defined."
        )


@dataclass
class CyclicDependencyDiagnostic(Diagnostic):
    """Diagnostic for cyclic dependencies in variables."""

    involved_variables: list[str]
    """ List of variables involved in the cycle."""

    @staticmethod
    def from_symbol(symbol: Symbol):
        """Create a CyclicDependencyDiagnostic from a Clingo symbol."""

        involved_symbols = asp_to_python_list(symbol.arguments[1])
        involved_symbols.reverse()

        return CyclicDependencyDiagnostic(involved_variables=[s.name for s in involved_symbols])

    def __str__(self):
        return f"Cycle detected involving the variables: [{', '.join(self.involved_variables)}]"


@dataclass
class UnsupportedOperatorDiagnostic(Diagnostic):
    """Diagnostic for unsupported operators."""

    operator: str
    """ The unsupported operator."""

    @staticmethod
    def from_symbol(symbol: Symbol):
        """Create an UnsupportedOperatorDiagnostic from a Clingo symbol."""

        return UnsupportedOperatorDiagnostic(operator=str(symbol.arguments[0]))

    def __str__(self):
        return f"Unsupported operator: {self.operator}"


@dataclass
class UnsupportedArgumentTypeDiagnostic(Diagnostic):
    """Diagnostic for unsupported argument types in operators."""

    operator: str
    """ The operator with unsupported argument types."""
    arguments: list[str]
    """ List of argument types used in the operation.

        At least one of these is wrong,
        but so far we do not know which one.
    """

    @staticmethod
    def from_symbol(symbol: Symbol):
        """Create an UnsupportedArgumentTypeDiagnostic from a Clingo symbol."""
        return UnsupportedArgumentTypeDiagnostic(
            operator=str(symbol.arguments[0]), arguments=[arg.name for arg in symbol.arguments[1].arguments]
        )

    def __str__(self):
        return f"Unsupported argument types for ({self.operator}): [{", ".join(self.arguments)}]"


def register_diagnostics(cls):
    """Decorator to attach _registry to Diagnostic after subclasses are defined.

    The registry is a mapping from DiagnosticType to the corresponding Diagnostic subclass
    and is used to create instances of diagnostics based on Clingo symbols.
    """
    cls._registry = {
        DiagnosticType.UNDEFINED_VARIABLE: UndefinedVariableDiagnostic,
        DiagnosticType.CYCLIC_DEPENDENCY: CyclicDependencyDiagnostic,
        DiagnosticType.UNSUPPORTED_OPERATOR_TYPE: UnsupportedOperatorDiagnostic,
        DiagnosticType.UNSUPPORTED_ARGUMENT_TYPE: UnsupportedArgumentTypeDiagnostic,
    }
    return cls


# This decorator is applied here because all used classes have to be defined first
Diagnostic = register_diagnostics(Diagnostic)
