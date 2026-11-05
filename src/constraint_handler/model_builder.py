"""Construct result atoms from evaluated constraint-handler variables."""

from collections.abc import Iterable
from typing import Any

import clingo

from constraint_handler import evaluator, multimap
from constraint_handler.PropagatorConstants import OTHER_ENGINE_VAR_NAME, ValueStatus
from constraint_handler.PropagatorVariables import BoolEvaluateVariable, EvaluateVariable, VariableType
from constraint_handler.schemas import expression, result, warning


class ModelBuilder:
    """Convert evaluated values and warnings into a fresh Python-side model."""

    def __init__(self, ignored_warnings: dict[warning.Kind, tuple[int, bool]]) -> None:
        """Initialize warning filtering.

        Args:
            ignored_warnings: Warning kinds mapped to their literal and active-ignore flag.
        """
        self.ignored_warnings = ignored_warnings
        self.atoms: set[result.ResultAtom] = set()

    def build(
        self,
        variables: Iterable[VariableType],
        evaluate_variables: Iterable[EvaluateVariable],
        errors: Iterable[warning.Warning],
    ) -> set[result.ResultAtom]:
        """Build a fresh model without changing variable or solver state.

        Args:
            variables: Variables whose values and warnings should be exported.
            evaluate_variables: Explicit expression evaluations to export.
            errors: Additional optimization and propagator warnings.

        Returns:
            A set of result atoms and non-ignored warnings.
        """
        self.atoms = set()
        for variable in variables:
            self.add_warnings(variable.get_errors())
            if isinstance(variable, BoolEvaluateVariable):
                continue
            if variable.name == OTHER_ENGINE_VAR_NAME:
                continue
            value = variable.get_value()
            if value is ValueStatus.NOT_SET:
                self.add_warnings(
                    [warning.Warning(warning.Propagator(), (str(variable),), "Variable has no value set in on_model!")]
                )
                continue
            if value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue
            self.add_value(variable.var, value)

        for variable in evaluate_variables:
            self.add_warnings(variable.get_errors())
            value = variable.get_value()
            if value is ValueStatus.NOT_SET:
                self.add_warnings(
                    [
                        warning.Warning(
                            warning.Propagator(), (str(variable),), "Evaluate variable has no value set in on_model!"
                        )
                    ]
                )
                continue
            if value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue
            reduced_value, reduction_errors = evaluator.reducedExpr(value)
            self.atoms.add(result.Evaluated(variable.ref, reduced_value))
            self.add_warnings(warning.Warning(kind, (), msg) for kind, msg in reduction_errors)

        self.add_warnings(errors)
        return self.atoms

    def add_value(self, symbol: clingo.Symbol, value: Any) -> None:
        """Dispatch a variable value to its result-atom conversion.

        Args:
            symbol: Variable symbol.
            value: Evaluated value to export.
        """
        assert value is not ValueStatus.NOT_SET, f"Variable {symbol} has no value set in on_model!"
        if isinstance(value, expression.constant | expression.Bad | tuple):
            reduced_value, errors = evaluator.reducedExpr(value)
            self.add_warnings(warning.Warning(kind, (), msg) for kind, msg in errors)
            self.atoms.add(result.Value(symbol, reduced_value))
        elif isinstance(value, (set, frozenset)):
            self.add_set(symbol, value)
        elif isinstance(value, (dict, multimap.Multimap)):
            self.add_multimap(symbol, value)
        else:
            print(f"Unknown variable type {type(value)} for variable {symbol} in on_model!")

    def add_set(self, symbol: clingo.Symbol, values: set | frozenset) -> None:
        """Convert a set value, retaining the existing bad-value fallback.

        Args:
            symbol: Variable symbol.
            values: Set elements to export.
        """
        try:
            reference = expression.Ref(evaluator.get_baseType(values), clingo.Function("variable", [symbol]))
            atoms = [result.Value(symbol, reference)]
            for value in values:
                assert value is not ValueStatus.NOT_SET, f"Set variable {symbol} has no value set in on_model!"
                element = value if value == expression.Bad.bad else expression.Val(evaluator.get_baseType(value), value)
                atoms.append(result.Set_value(symbol, element))
            self.atoms.update(atoms)
        except Exception:
            self.add_warnings([warning.Warning(warning.Variable(warning.VariableWarning.badValue), (), symbol)])
            self.atoms.add(result.Value(symbol, expression.Bad.bad))

    def add_multimap(self, symbol: clingo.Symbol, values: dict | multimap.Multimap) -> None:
        """Convert multimap keys and their values to result atoms.

        Args:
            symbol: Variable symbol.
            values: Mapping from keys to collections of values.
        """
        if values == expression.Bad.bad:
            reference = values
        else:
            try:
                reference = expression.Val(evaluator.get_baseType(values), symbol)
            except Exception:
                reference = expression.Bad.bad
        self.atoms.add(result.Value(symbol, reference))
        if reference != expression.Bad.bad:
            errors = []
            for key, entries in values.items():
                assert (
                    entries is not ValueStatus.NOT_SET
                ), f"Dict variable {symbol} has key {key} with no value set in on_model!"
                for entry in entries:
                    reduced_key, key_errors = evaluator.reducedExpr(key)
                    reduced_entry, entry_errors = evaluator.reducedExpr(entry)
                    errors.extend(key_errors)
                    errors.extend(entry_errors)
                    self.atoms.add(result.Multimap_value(symbol, reduced_key, reduced_entry))
            self.add_warnings(warning.Warning(kind, (), msg) for kind, msg in errors)

    def add_warnings(self, errors: Iterable[warning.Warning]) -> None:
        """Add warnings unless their ignore literal is active.

        Args:
            errors: Warnings to filter and export.
        """
        for error in errors:
            ignored = self.ignored_warnings.get(error.id)
            if ignored is None or not ignored[1]:
                self.atoms.add(error)
                self.atoms.update(
                    (
                        warning.Warning_raised0(),
                        warning.Warning_raised1(error.id),
                        warning.Warning_raised2(error.id, error.declarations),
                    )
                )
