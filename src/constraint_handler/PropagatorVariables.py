from __future__ import annotations

import sys
from abc import abstractmethod
from typing import Any, Iterable, Protocol

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning
import constraint_handler.solver_environment as solver_environment
from constraint_handler.PropagatorConstants import (
    DEBUG_PRINT,
    DEFAULT_DECISION_LEVEL,
    EXECUTION_INPUT,
    EXECUTION_OUTPUT,
    FALSE_ASSIGNMENTS,
    EvaluationResult,
    ValueStatus,
    propagator_warning_t,
)


def myprint(*args: tuple, **kwargs: dict[str, Any]):
    """Print debug output when debugging is enabled.

    This helper is a thin wrapper around ``print`` controlled by the
    ``DEBUG_PRINT`` constant.

    Args:
        *args: Positional arguments passed to ``print``.
        **kwargs: Keyword arguments passed to ``print``.
    """
    if DEBUG_PRINT:
        print(*args, **kwargs)


class VariableType(Protocol):
    """
    Protocol for variable types used in the propagator. Defines the required interface for variables.
    """

    name: str

    @property
    @abstractmethod
    def var(self) -> clingo.Symbol: ...
    @property
    @abstractmethod
    def decision_level(self) -> int: ...
    @property
    @abstractmethod
    def parents(self) -> list[VariableType]: ...

    @property
    @abstractmethod
    def literals(self) -> set[int]: ...

    @abstractmethod
    def has_domain(self) -> bool: ...

    @abstractmethod
    def has_unassigned(self) -> bool: ...

    @abstractmethod
    def get_value(self) -> Any: ...

    @abstractmethod
    def reset(self, dl: int) -> None: ...

    @abstractmethod
    def get_errors(self) -> propagator_warning_t: ...

    @abstractmethod
    def vars(self) -> set[clingo.Symbol]: ...

    @abstractmethod
    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult: ...

    @abstractmethod
    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None: ...


class VariableValue:
    """
    Represents a single expression appearing in an assignment atom.

    Attributes:
        expr: The expression to evaluate.
        value: The current value of the expression.
        literal: The associated literal.
        assigned: Whether the literal is assigned.
        decision_level: The decision level at which the value was set.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, expr: expression.Expr, lit: int):
        """
        Initialize a VariableValue.

        Args:
            expr: Expression associated with the variable.
            lit: The literal controlling whether this expression is evaluated.
        """
        self.expr: expression.Expr = expr
        self.value: Any = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.errors: propagator_warning_t = []

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """
        Evaluate the expression

        Args:
            evaluations: Current variable evaluations.
            ctl: PropagateControl for checking literal assignments and decision levels.
            env: Environment for evaluation.

        Returns:
            bool: True if the value has changed, False otherwise.
        """
        self.assigned = ctl.assignment.value(self.literal)

        if ctl.assignment.value(self.literal) is None:
            assert self.value == ValueStatus.NOT_SET
            return False

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return False

        elif ctl.assignment.is_false(self.literal):
            # Assignment is false, so value is false assignment
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            self.decision_level = ctl.assignment.decision_level
            return True

        for var in self.vars():
            if var not in evaluations and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.value == ValueStatus.NOT_SET
                return False

        self.value, errors = evaluator.evaluate_expr(self.expr, env, evaluations)

        for error, msg in errors:
            self.errors.append(warning.Warning(error, (), repr(msg)))

        myprint(f"{self.expr} evaluated to {self.value}")

        self.decision_level = ctl.assignment.decision_level
        return True

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected while evaluating this value.

        Returns:
            propagator_warning_t: List of warnings.
        """
        return self.errors

    def vars(self) -> frozenset[clingo.Symbol]:
        """
        Collect variables referenced by the underlying expression.

        Returns:
            frozenset[clingo.Symbol]: Variables referenced by ``self.expr``.
        """
        return evaluator.collectVars(self.expr)

    def reset(self, dl: int):
        """
        Reset based on decision level.

        Args:
            dl: Decision level threshold.
        """
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.assigned = None
            self.errors = []

    @property
    def literals(self) -> set[int]:
        """
        Return the literal that represents the current value.

        Returns:
            set[int]: A singleton set containing the signed literal if assigned; otherwise empty.
        """
        if self.value != ValueStatus.NOT_SET:
            if self.assigned:
                return {self.literal}
            else:
                return {-self.literal}

        return set()

    def __eq__(self, other) -> bool:
        if not isinstance(other, VariableValue):
            return False
        return self.expr == other.expr

    def __hash__(self) -> int:
        return hash(str(self.expr))

    def __str__(self) -> str:
        return f"VariableValue({self.expr}, {self.value})"

    def __repr__(self) -> str:
        return f"VariableValue({self.expr}, {self.value})"


class EvaluateVariable:
    """
    Represents an evaluate atom defined by an operator and arguments of the operator.

    Attributes:
        op: The operator for the expression.
        args: List of argument expressions.
        value: The current value of the evaluation.
        literal: The associated literal.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, op: expression.Operator, args: list[expression.Expr], literal: int = -1):
        """
        Initialize an EvaluateVariable.

        Args:
            op: Operator to apply.
            args: Operands for the operator.
            literal: Literal controlling whether this operation is active.
        """
        self.op: expression.Operator = op
        self.args: list[expression.Expr] = args
        self.value: Any = ValueStatus.NOT_SET
        self.literal: int = literal

        self.errors: propagator_warning_t = []

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """
        Evaluate the expression

        Args:
            evaluations: Current variable evaluations.
            ctl: PropagateControl for checking literal assignments and decision levels.
            env: Environment for evaluation.

        Returns:
            bool: True if the value has changed, False otherwise.
        """
        if not ctl.assignment.is_true(self.literal):
            return False
        myprint(f"Evaluating {self.op}({self.args})")
        value, errors = evaluator.evaluate_expr(expression.Operation(self.op, self.args), env, evaluations)
        self.value = value
        for error, msg in errors:
            self.errors.append(warning.Warning(error, (), repr(msg)))
        return True

    def get_value(self) -> Any:
        """
        Return the current value of the evaluation.

        Returns:
            Any: Current value.
        """
        return self.value

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected while evaluating this operation.

        Returns:
            propagator_warning_t: List of warnings.
        """
        return self.errors

    def __eq__(self, other) -> bool:
        if not isinstance(other, EvaluateVariable):
            return False
        return self.op == other.op and self.args == other.args and self.literal == other.literal

    def __hash__(self) -> int:
        return hash((str(self.op), str(self.args), self.literal))

    def __str__(self) -> str:
        return f"EvaluateVariable({self.op}, {self.args})"

    def __repr__(self) -> str:
        return self.__str__()


class EnsureVariable:
    """
    Represents an 'ensure' atom, which ensures a certain expression holds.
    Implements the VariableType protocol.

    Attributes:
        name: Name of the ensure atom.
        expression: The VariableValue instance being ensured.
        value: Current value of the expression.
        decision_level: Decision level at which the value was set.
    """

    # used to define the variable for ensure variables
    # __c serves as an ID and is incremented in every __init__ call
    __var = "ensure"
    __c = 0

    def __init__(self, name: str, expr: expression.Expr, literal: int):
        """
        Initialize an EnsureVariable.

        Args:
            name: Name of the ensure atom.
            expr: Expression that must hold.
            literal: Literal controlling whether the ensure atom is active.
        """
        self.name: str = name
        self.expression: VariableValue = VariableValue(expr, literal)

        self.value: ValueStatus | bool = ValueStatus.NOT_SET
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.var = clingo.Function(EnsureVariable.__var, [clingo.Number(EnsureVariable.__c)])
        EnsureVariable.__c += 1

    @property
    def parents(self) -> list[VariableType]:
        """
        Return parent variables.

        Returns:
            list[VariableType]: Empty list (ensure variables have no parents).
        """
        return []

    def has_domain(self) -> bool:
        """
        Return whether the variable has a domain.

        Returns:
            bool: Always True for ensure variables.
        """
        return True

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict.
        """
        if self.expression.assigned is not None and not self.expression.assigned:
            # Ensure is false, so no conflict
            return EvaluationResult.NOT_CHANGED

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        changed = self.expression.evaluate(evaluations, ctl, env)

        if not changed:
            return EvaluationResult.NOT_CHANGED

        self.value = self.expression.value
        self.decision_level = ctl.assignment.decision_level
        # assert isinstance(self.value, bool), "EnsureVariable evaluated to non-boolean value"

        conflict = self.value is False or self.value is None
        if conflict:
            return EvaluationResult.CONFLICT

        return EvaluationResult.CHANGED

    def get_value(self) -> ValueStatus | bool:
        """
        Return the current value of the ensure variable.

        Returns:
            ValueStatus | bool: Current value, or NOT_SET.
        """
        return self.value

    def has_unassigned(self) -> bool:
        """
        Check whether the ensure variable is unassigned.

        Returns:
            bool: True if the value is NOT_SET.
        """
        return self.value == ValueStatus.NOT_SET

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect variables referenced by the ensure expression.

        Returns:
            set[clingo.Symbol]: Variables referenced by the expression.
        """
        return set(self.expression.vars())

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected during evaluation.

        Returns:
            propagator_warning_t: List of warnings.
        """
        return self.expression.get_errors()

    @property
    def literals(self) -> set[int]:
        """
        Return signed literals that give the current value of the ensure variable.

        Returns:
            set[int]: Set of signed literals.
        """
        return self.expression.literals

    def reset(self, dl: int) -> None:
        """
        Reset based on the decision level.

        Args:
            dl: Decision level threshold.
        """
        self.expression.reset(dl)
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET
            self.decision_level = DEFAULT_DECISION_LEVEL

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        """
        Does nothing, as ensure variables are not added to the evaluation dictionary.
        This is here for compatibility with the VariableType protocol.

        Args:
            d: Dictionary to update.
        """
        return

    def __hash__(self):
        return hash((self.name, self.expression))

    def __repr__(self) -> str:
        return f"EnsureVariable(name={self.name}, expression={self.expression})"


class Variable:
    """
    A variable with a name and a value expression.

    Class to hold the expressions assigned to a variable (via variable_define, variable_declare, etc).
    It also evaluates them and discerns the appropriate value for the variable,
    while keeping track of the decision level and errors.

    Implements the VariableType protocol.

    Attributes:
        name: Name of the variable.
        var: Clingo symbol for the variable.
        expressions: Set of possible values (VariableValue).
        value: Current value of the variable.
        parents: Parent variables.
        decision_level: Decision level at which the value was set.
        domain_literals: Literals defining the domain.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, name: str, var: clingo.Symbol):
        """
        Initialize a Variable.

        Args:
            name: Name for the variable.
            var: Clingo symbol representing this variable.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: set[VariableValue] = set()
        self.value: Any = ValueStatus.NOT_SET
        self.parents: list[VariableType] = []
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        # literals for atoms that can define a domain
        # (variable_define, variable_declare, variable_optinal)
        self.domain_literals: set[int] = set()

        self.errors: propagator_warning_t = []

    def add_value(self, expr: expression.Expr, value_lit: int, domain_lit: int) -> None:
        """
        Add a possible value expression for this variable.

        Args:
            expr: Expression representing a candidate value.
            value_lit: Literal for the value assignment.
            domain_lit: Literal indicating the truth value of the domain/declaration context.
        """
        self.expressions.add(VariableValue(expr, value_lit))
        self.domain_literals.add(domain_lit)

    def get_value(self) -> Any:
        """
        Return the current value.

        Returns:
            Any: Current value, or a ValueStatus.
        """
        return self.value

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected while evaluating candidate values.

        Returns:
            propagator_warning_t: List of warnings.
        """
        errors: propagator_warning_t = []
        for var_value in self.expressions:
            errors.extend(var_value.get_errors())
        return errors

    def has_unassigned(self) -> bool:
        """
        Check whether any candidate value is still unassigned.

        Returns:
            bool: True if any candidate value is NOT_SET.
        """
        return any(var_value.value == ValueStatus.NOT_SET for var_value in self.expressions)

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect variables referenced by all candidate value expressions.

        Returns:
            set[clingo.Symbol]: Referenced variables.
        """
        vars = set()
        for value in self.expressions:
            vars.update(value.vars())
        return vars

    def has_domain(self) -> bool:
        """
        Return whether at least one value expression is available.

        Returns:
            bool: True if any candidate expression exists.
        """
        return len(self.expressions) > 0

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return an EvaluationResult.
        """
        changed = False
        for value in self.expressions:
            changed |= value.evaluate(evaluations, ctl, env)

        if not changed:
            return EvaluationResult.NOT_CHANGED

        # if some value changed, we need to discern the new value
        val = self.get_values()
        if len(val) > 1:
            # multiple values assigned to the same variable
            # this is True even if the same value is assigned multiple times
            myprint(f"Variable vals: {val}")
            self.decision_level = ctl.assignment.decision_level
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            return EvaluationResult.CONFLICT
        elif len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                val = [ValueStatus.NOT_SET]

            # if at least one domain lit is true, then a value MUST be chosen
            elif any(ctl.assignment.is_true(domain_lit) for domain_lit in self.domain_literals):
                # if all values are set and none are true, then it is set to false assignment
                # And there is a conflict, as a having a domain true, means that the variable MUST have a value
                self.decision_level = ctl.assignment.decision_level
                self.value = ValueStatus.ASSIGNMENT_IS_FALSE
                return EvaluationResult.CONFLICT
            else:
                # if no domain lit is true, then we can treat it as false
                val = [ValueStatus.ASSIGNMENT_IS_FALSE]

        elif len(val) == 1:
            if val[0] == self.value:
                # same value as before
                return EvaluationResult.NOT_CHANGED

        self.decision_level = ctl.assignment.decision_level
        self.value = val[0]
        if sum(ctl.assignment.is_true(domain_lit) for domain_lit in self.domain_literals) > 1:
            # In this instance we add a warning to say that a value was chosen out of multiple domains
            self.errors.append(
                warning.Warning(
                    warning.Variable(warning.VariableWarning.multipleDeclarations),  # ty:ignore[unresolved-attribute]
                    (self.var,),
                    f"Multiple domain literals are true for variable {self.var}",
                )
            )
        return EvaluationResult.CHANGED

    def get_values(self) -> list[Any]:
        """
        Return all concrete values assigned to this variable.

        Returns:
            list[Any]: Values excluding NOT_SET and ASSIGNMENT_IS_FALSE.
        """
        vals = [
            value.value
            for value in self.expressions
            if value.value != ValueStatus.NOT_SET and value.value != ValueStatus.ASSIGNMENT_IS_FALSE
        ]
        return vals

    @property
    def literals(self) -> set[int]:
        """
        Return signed literals implied by all candidate values.

        Returns:
            set[int]: Set of signed literals.
        """
        lits = set()
        for value in self.expressions:
            lits.update(value.literals)
        return lits

    def reset(self, dl: int) -> None:
        """
        Reset based on decision level.

        Args:
            dl: Decision level threshold.
        """
        for value in self.expressions:
            value.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        """
        Add this variable's value to the evaluation dictionary.

        Args:
            d: Dictionary to update.
        """
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore
            return

        d[self.var] = value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Variable):
            return False
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self) -> int:
        return hash((self.var, frozenset(self.expressions)))

    def __str__(self) -> str:
        return f"Variable({self.name}, {self.var}, {self.expressions})"

    def __repr__(self) -> str:
        return f"Variable({self.name}, {self.var}, {self.expressions})"


class SetVariableValue:
    """
    Represents a set of possible values for a set variable.

    Attributes:
        values: Set of VariableValue instances representing possible values.
    """

    def __init__(self) -> None:
        """Initialize a SetVariableValue."""
        self.values: set[VariableValue] = set()

    def has_domain(self) -> bool:
        """
        Return whether at least one value expression is present.

        Returns:
            bool: True if any value expression exists.
        """
        return len(self.values) > 0

    def add_value(self, arg: expression.Expr, lit: int) -> None:
        """
        Add a candidate value to the set.

        Args:
            arg: Expression for a set element.
            lit: Literal guarding the element.
        """
        self.values.add(VariableValue(arg, lit))

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected while evaluating set elements.

        Returns:
            propagator_warning_t: List of warnings.
        """
        errors: propagator_warning_t = []
        for var_value in self.values:
            errors.extend(var_value.get_errors())
        return errors

    @property
    def literals(self) -> set[int]:
        """
        Return signed literals implied by currently evaluated set elements.

        Returns:
            set[int]: Set of signed literals.
        """
        lits = set()
        for value in self.values:
            lits.update(value.literals)
        return lits

    def get_value(self) -> ValueStatus | frozenset[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        if self.has_unassigned():
            return ValueStatus.NOT_SET
        # Note that we let None be a part of the set!
        return frozenset(arg.value for arg in self.values if arg.value != ValueStatus.ASSIGNMENT_IS_FALSE)

    def has_unassigned(self) -> bool:
        """
        Check whether any element value is still unassigned.

        Returns:
            bool: True if any element is NOT_SET.
        """
        return any(arg.value == ValueStatus.NOT_SET for arg in self.values)

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect variables referenced by all set element expressions.

        Returns:
            set[clingo.Symbol]: Referenced variables.
        """
        vars = set()
        for arg in self.values:
            vars.update(arg.vars())
        return vars

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        changed = False
        for arg in self.values:
            changed |= arg.evaluate(evaluations, ctl, env)

        return changed

    def reset(self, dl: int) -> None:
        """
        Reset all element values based on decision level.

        Args:
            dl: Decision level threshold.
        """
        for arg in self.values:
            arg.reset(dl)

    def __eq__(self, other) -> bool:
        if not isinstance(other, SetVariableValue):
            return False
        return self.values == other.values

    def __hash__(self) -> int:
        return hash(frozenset(self.values))

    def __str__(self) -> str:
        return f"SetVariableValue({self.values})"

    def __repr__(self) -> str:
        return self.__str__()


class SetVariable:
    """
    A set variable with a name and a set of value expressions.

    This is supposed to mirror the set_declare/2 and set_assign/3 atom in the ASP encoding.
    set_declare is this class, while each set_assign adds a possible value to the set.

    Implements the VariableType protocol.

    Attributes:
        name: Name of the set variable.
        var: Clingo symbol for the variable.
        expressions: SetVariableValue instance holding possible values.
        value: Current value of the set variable.
        literal: Literal for the set declaration.
        assigned: Truth value of the set declaration.
        decision_level: Decision level of the set declaration.
        parents: Parent variables.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        """
        Initialize a SetVariable.

        Args:
            name: Name of the set variable.
            var: Clingo symbol identifying the variable.
            lit: Literal for the set declaration.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: SetVariableValue = SetVariableValue()

        self.value: ValueStatus | frozenset[Any] = ValueStatus.NOT_SET

        self.literal: int = lit  # this is the literal for the set declaration
        self.assigned: bool | None = None  # Truth value of the set declaration
        self.decision_level: int = DEFAULT_DECISION_LEVEL  # decision level of the set declaration

        self.parents: list[VariableType] = []

        self.errors: propagator_warning_t = []

    def has_domain(self) -> bool:
        """
        Check whether the set has a domain.

        Returns:
            bool: True if at least one value can be assigned.
        """
        return self.expressions.has_domain()

    def add_value(self, arg: expression.Expr, lit: int) -> None:
        """
        Add a potential value expression to the set.

        Args:
            arg: Expression representing one possible set element.
            lit: Literal for the corresponding `set_assign/3` atom.
        """
        self.expressions.add_value(arg, lit)

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings/errors collected during evaluation.

        Returns:
            propagator_warning_t: Warnings and errors for this set and its elements.
        """
        return self.expressions.get_errors() + self.errors

    @property
    def literals(self) -> set[int]:
        """
        Return literals relevant for this variable's current state.

        Includes literals from all element assignments and, if assigned,
        the set declaration literal.

        Returns:
            set[int]: Set of literals.
        """
        lits = self.expressions.literals
        if self.assigned is not None:
            if self.assigned:
                lits.add(self.literal)
            else:
                lits.add(-self.literal)
        return lits

    def get_value(self) -> ValueStatus | frozenset[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        return self.value

    def has_unassigned(self) -> bool:
        """
        Check whether any element expression is still unassigned.

        Returns:
            bool: True if at least one element is unassigned.
        """
        return self.expressions.has_unassigned()

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables referenced by this set.

        Returns:
            set[clingo.Symbol]: Variables used in element expressions.
        """
        return self.expressions.vars()

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return an EvaluationResult.
        """
        self.assigned = ctl.assignment.value(self.literal)

        if self.assigned is None:
            return EvaluationResult.NOT_CHANGED

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        elif ctl.assignment.is_false(self.literal):
            # Assignment is false, so value is set to false assignment
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            self.decision_level = ctl.assignment.decision_level
            self.errors.append(
                warning.Warning(
                    warning.ExpressionWarning.syntaxError, (self.var,), "Set declaration is False"
                )  # ty:ignore[unresolved-attribute]
            )
            return EvaluationResult.CHANGED

        changed = self.expressions.evaluate(evaluations, ctl, env)

        if changed or not self.has_unassigned():
            self.value = self.expressions.get_value()
            if self.value != ValueStatus.NOT_SET:
                # only update decision level if we have a value
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.CHANGED

        # if nothing changed or the changes did not lead to a value
        return EvaluationResult.NOT_CHANGED

    def reset(self, dl: int) -> None:
        """
        Reset based on decision level.

        Args:
            dl: Decision level threshold.
        """
        self.expressions.reset(dl)
        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        """
        Add this variable's value into an output dictionary.

        Args:
            d: Dictionary to update.
        """
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore
            return

        d[self.var] = value

    def __eq__(self, value) -> bool:
        if not isinstance(value, SetVariable):
            return False
        return self.var == value.var and self.expressions == value.expressions

    def __hash__(self) -> int:
        return hash((self.var, self.expressions))

    def __str__(self) -> str:
        return f"SetVariable({self.name}, {self.var})"

    def __repr__(self) -> str:
        return self.__str__()


class DictVariable:
    """
    A dict variable with a name and a set of key-value expressions.

    This is supposed to mirror the multimap_declare/2 and multimap_assign/4 atom in the ASP encoding.
    multimap_declare is this class, while each multimap_assign adds a possible key-value pair to the dict.

    Implements the VariableType protocol.

    Attributes:
        name: Name of the dict variable.
        var: Clingo symbol for the variable.
        expressions: Dictionary mapping keys to SetVariableValue instances.
        value: Current value of the dict variable.
        literal: Literal for the dict declaration.
        assigned: Truth value of the dict declaration.
        decision_level: Decision level of the current value.
        parents: Parent variables.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        """
        Initialize a DictVariable.

        Args:
            name: Name of the dict variable.
            var: Clingo symbol identifying the variable.
            lit: Literal for the dict declaration.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: dict[VariableValue, SetVariableValue] = multimap.HashableDict()

        self.value: ValueStatus | dict[clingo.Symbol, Any] = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.parents: list[VariableType] = []

        self.errors: propagator_warning_t = []

    def add_value(self, key: expression.Expr, expr: expression.Expr, lit: int) -> None:
        """
        Add a key-value pair to the dict variable.

        Args:
            key: Expression for the key.
            expr: Expression for the value.
            lit: Literal for assignment.
        """
        # setting lit for key to 1 since it does not have its own literal
        # the literal is bound for the value!
        key_val = VariableValue(key, 1)
        if key_val not in self.expressions:
            self.expressions[key_val] = SetVariableValue()
        self.expressions[key_val].add_value(expr, lit)

    def has_domain(self) -> bool:
        """
        Check if the dict variable has a domain (any key-value pairs).

        Returns:
            bool: True if there are key-value pairs, False otherwise.
        """
        return len(self.expressions) > 0

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from the dict variable and its key-value pairs.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        errors: propagator_warning_t = []
        for key, value in self.expressions.items():
            errors.extend(key.get_errors())
            errors.extend(value.get_errors())
        return errors + self.errors

    @property
    def literals(self) -> set[int]:
        """
        Return literals relevant for this variable's current state.

        Includes literals from all key/value expressions and, if assigned,
        the dict declaration literal.

        Returns:
            set[int]: Set of literals.
        """
        lits = set()
        for key, value in self.expressions.items():
            lits.update(value.literals)
            lits.update(key.literals)

        if self.assigned is not None:
            if self.assigned:
                lits.add(self.literal)
            else:
                lits.add(-self.literal)

        return lits

    def get_value(self) -> ValueStatus | dict[clingo.Symbol, Any]:
        """
        Get the current value of the dict variable.

        Returns:
            ValueStatus | dict[clingo.Symbol, Any]: Current dict value or NOT_SET.
        """
        return self.value

    def discern_value(self) -> ValueStatus | dict[clingo.Symbol, Any]:
        """
        Returns a dictionary mapping keys to their assigned values.
        If any value is unassigned, returns None for that key.
        """
        result = multimap.HashableDict()
        for key, value in self.expressions.items():
            key_val = key.value
            val = value.get_value()
            if val == ValueStatus.NOT_SET or key_val == ValueStatus.NOT_SET:
                # If any value is not set,
                # then whole dict is not set
                return ValueStatus.NOT_SET
            elif val == ValueStatus.ASSIGNMENT_IS_FALSE or len(val) == 0:
                # If the value is false assignment or empty set,
                # then we treat it as not present in the dict
                # TODO: check if this is the desired behavior
                continue

            result[key_val] = val
        return result

    def has_unassigned(self) -> bool:
        """
        Check whether any key/value expression is still unassigned.

        Returns:
            bool: True if any key/value expression is unassigned.
        """
        return any(key.assigned is None or value.has_unassigned() for key, value in self.expressions.items())

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables referenced by this dict.

        Returns:
            set[clingo.Symbol]: Variables used in key/value expressions.
        """
        vars = set()
        for key, value in self.expressions.items():
            vars.update(value.vars())
            vars.update(key.vars())
        return vars

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate all values in the dictionary and return (changed, conflict).
        For DictVariable, conflict should never occur.
        """

        self.assigned = ctl.assignment.value(self.literal)

        if self.assigned is None:
            return EvaluationResult.NOT_CHANGED

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        elif ctl.assignment.is_false(self.literal):
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            self.decision_level = ctl.assignment.decision_level
            self.errors.append(
                warning.Warning(warning.ExpressionWarning.syntaxError, (self.var,), "Dict declaration is False")  # type: ignore[unresolved-attribute]
            )
            return EvaluationResult.CHANGED

        changed = False
        for key, value in self.expressions.items():
            changed |= key.evaluate(evaluations, ctl, env)
            changed |= value.evaluate(evaluations, ctl, env)

        if changed or not self.has_unassigned():
            self.value = self.discern_value()
            if self.value != ValueStatus.NOT_SET:
                # only update decision level if we have a value
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.CHANGED

        # if nothing changed or the changes did not lead to a value
        return EvaluationResult.NOT_CHANGED

    def reset(self, dl: int) -> None:
        """
        Reset based on the decision level.

        Args:
            dl: Decision level threshold.
        """
        for key, value in self.expressions.items():
            key.reset(dl)
            value.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        """
        Add this variable's value into the given dictionary.

        Args:
            d: Dictionary to update.
        """
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore
            return

        d[self.var] = value

    def __eq__(self, other) -> bool:
        if not isinstance(other, DictVariable):
            return False
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self) -> int:
        return hash((self.var, frozenset(self.expressions.items())))

    def __str__(self) -> str:
        return f"DictVariable({self.name}, {self.var})"

    def __repr__(self) -> str:
        return self.__str__()


class OptimizationSum:
    """
    Represents a sum for optimization purposes, holding expressions and their priorities.

    Attributes:
        expressions: List of (clingo.Symbol, VariableValue) pairs.
                    The symbol is the variable associated with the expresssion.
                    The value of the expression is what is used in the sum.
        value: The current sum value.
        priority: Priority of the optimization sum.
        decision_level: Decision level at which the value was set.
    """

    def __init__(self, priority: int = 0) -> None:
        """
        Initialize an OptimizationSum.

        Args:
            priority: Priority of the optimization sum.
        """
        self.expressions: list[tuple[clingo.Symbol, VariableValue]] = []
        self.value: int | float = -sys.maxsize
        self.priority: int = priority
        self.decision_level: int = DEFAULT_DECISION_LEVEL

    def add_value(self, var: clingo.Symbol, expr: expression.Expr, lit: int) -> None:
        """
        Add a value to the optimization sum.

        Args:
            var: Clingo symbol for the variable.
            expr: Expression to evaluate.
            lit: Associated literal.
        """
        self.expressions.append((var, VariableValue(expr, lit)))

    @property
    def literals(self) -> set[int]:
        """
        Get all literals associated with the optimization sum that gave it its current value.

        Returns:
            set[int]: Set of literals.
        """
        lits = set()
        for var, expr in self.expressions:
            lits.update(expr.literals)
        return lits

    def discern_value(self) -> int | float:
        """
        Compute the sum of all assigned values in the optimization sum.

        Returns:
            int | float: The sum of all assigned values.
        """
        vals = set()
        for var, expr in self.expressions:
            myprint(f"Summing {expr} with value {expr.value}")
            if (
                expr.value != ValueStatus.NOT_SET
                and expr.value != ValueStatus.ASSIGNMENT_IS_FALSE
                and expr.value is not None
            ):
                vals.add((var, expr.value))

        return sum(value for var, value in vals)

    def get_value(self) -> int | float:
        """
        Get the current value of the optimization sum.

        Returns:
            int | float: The sum value.
        """
        return self.value

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from the evaluation of the optimization sum.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        errors: propagator_warning_t = []
        for _, expr in self.expressions:
            errors.extend(expr.get_errors())
        return errors

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """
        Evaluate the optimization sum and return True if the value has changed.

        Args:
            evaluations: Current variable evaluations.
            ctl: Clingo propagate control.
            env: Evaluation environment.

        Returns:
            bool: True if the value has changed, False otherwise.
        """
        changed = False

        for var, expr in self.expressions:
            changed |= expr.evaluate(evaluations, ctl, env)

        if changed:
            total = self.discern_value()
            if total != self.value:
                self.decision_level = ctl.assignment.decision_level
                self.value = total
                return True

        return False

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables used in the optimization sum.

        Returns:
            set[clingo.Symbol]: Set of variables in the optimization sum.
        """
        vars = set()
        for var, expr in self.expressions:
            vars.update(expr.vars())
        return vars

    def reset(self, dl: int):
        """
        Reset the optimization sum if the decision level is greater than or equal to dl.

        Args:
            dl: Decision level threshold.
        """
        for var, expr in self.expressions:
            expr.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = -sys.maxsize

    def has_unassigned(self) -> bool:
        """
        Check if any value in the optimization sum is unassigned.

        Returns:
            bool: True if any value is unassigned, False otherwise.
        """
        return any(expr.value == ValueStatus.NOT_SET for var, expr in self.expressions)

    def __repr__(self) -> str:
        return f"OptimizationSum({self.expressions})"


class OptimizationHandler:
    """
    Handles multiple optimization sums, each with a priority.

    Attributes:
        sums: List of OptimizationSum instances.
              Note that this is a list and not a dict.
              OptimizationSums are ordered by priority, with higher priority sums coming first.
    """

    def __init__(self):
        """
        Initialize an OptimizationHandler.
        """
        self.sums: list[OptimizationSum] = []

    def add_value(self, var: clingo.Symbol, expr: expression.Expr, lit: int, priority: int = 0) -> None:
        """
        Add a value to the appropriate optimization sum by priority.

        Args:
            var: Clingo symbol for the variable.
            expr: Expression to evaluate.
            lit: Associated literal.
            priority: Priority of the optimization sum.
        """
        for _sum in self.sums:
            if _sum.priority == priority:
                _sum.add_value(var, expr, lit)
                return
        new_sum = OptimizationSum(priority)
        new_sum.add_value(var, expr, lit)
        self.sums.append(new_sum)

        self.sums.sort(key=lambda x: x.priority, reverse=True)  # higher priority first

    def get_sum_count(self) -> int:
        """
        Get the number of optimization sums.

        Returns:
            int: Number of optimization sums.
        """
        return len(self.sums)

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """
        Evaluate all optimization sums and return True if any value has changed.

        Args:
            evaluations: Current variable evaluations.
            ctl: Clingo propagate control.
            env: Evaluation environment.

        Returns:
            bool: True if any value has changed, False otherwise.
        """
        changed = False
        for _sum in self.sums:
            changed |= _sum.evaluate(evaluations, ctl, env)
        return changed

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables used in all optimization sums.

        Returns:
            set[clingo.Symbol]: Set of variables in all optimization sums.
        """
        vars = set()
        for _sum in self.sums:
            vars.update(_sum.vars())
        return vars

    def reset(self, dl: int):
        """
        Reset all optimization sums.

        Args:
            dl: Decision level threshold.
        """
        for _sum in self.sums:
            _sum.reset(dl)

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from all optimization sums.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        errors: propagator_warning_t = []
        for _sum in self.sums:
            errors.extend(_sum.get_errors())
        return errors

    def get_value(self) -> list[int | float]:
        """
        Get the values of all optimization sums ordered by priority.

        Returns:
            list[int | float]: List of current sum values.
        """
        return [_sum.get_value() for _sum in self.sums]

    def has_unassigned(self, position: int) -> bool:
        """
        Check if the optimization sum at the given position has unassigned values.

        Args:
            position: Index of the optimization sum (sorted by priority).

        Returns:
            bool: True if there are unassigned values, False otherwise.
        """
        return self.sums[position].has_unassigned()


class Execution:
    """
    Represents an execution block, holding statements and input/output variables.

    Implements the VariableType protocol.

    Attributes:
        name: Name of the execution.
        func_name: Clingo symbol for the function name.
        statements: List of ExecutionStatement instances.
        in_vars: List of input variable symbols.
        converted_in_vars: List of converted input variable symbols.
        out_vars: List of output variable symbols.
        converted_out_vars: List of converted output variable symbols.
        literal: Literal for the execution run atom.
        assigned: Truth value of the execution run atom.
        decision_level: Decision level of the execution.
        values: Current values of the execution outputs.
        parents: Parent variables.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(
        self,
        name: str,
        func_name: clingo.Symbol,
        in_vars: list[clingo.Symbol],
        out_vars: list[clingo.Symbol],
    ):
        """
        Initialize an Execution.

        Args:
            name: Name of the execution.
            func_name: Clingo symbol for the function name.
            in_vars: List of input variable symbols.
            out_vars: List of output variable symbols.
        """
        self.name: str = name
        self.func_name: clingo.Symbol = func_name
        self.statements: list[ExecutionStatement] = []
        self.in_vars: list[clingo.Symbol] = in_vars
        self.converted_in_vars: list[clingo.Symbol] = self.convert_vars(in_vars, input=True)
        self.out_vars: list[clingo.Symbol] = out_vars
        self.converted_out_vars: list[clingo.Symbol] = self.convert_vars(out_vars, input=False)

        # this is for the execution run atom
        self.literal: int = -1
        self.assigned: bool | None = None

        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.values: ValueStatus | list[tuple[clingo.Symbol, Any]] = ValueStatus.NOT_SET

        self.parents: list[VariableType] = []

        self.errors: propagator_warning_t = []

    def add_statement(self, stmt: statement.Stmt, lit: int) -> None:
        """
        Add a statement to the execution.

        Args:
            stmt: Statement to add.
            lit: Associated literal.
        """
        self.statements.append(ExecutionStatement(stmt, lit))

    def has_domain(self) -> bool:
        """
        Check if the execution has any statements (domain).

        Returns:
            bool: True if there are statements, False otherwise.
        """
        return len(self.statements) > 0

    def has_unassigned(self) -> bool:
        """
        Check if the execution has a value assigned to its outputs.

        Returns:
            bool: True if unassigned, False otherwise.
        """
        return self.values == ValueStatus.NOT_SET

    @property
    def var(self) -> clingo.Symbol:
        """
        Get the function name symbol for the execution.
        Note that the variables used inside the execution are local to the execution,
        hence, they do not get returned here.

        Returns:
            clingo.Symbol: Function name symbol.
        """
        return self.func_name

    @property
    def literals(self) -> set[int]:
        """
        Return the literal(s) associated with this execution.
        If the execution is run return the positive literal.
        If the execution is not run return the negative literal.
        If the execution is unassigned return an empty set.
        Also add the literals of the statements in the execution.

        Returns:
            set[int]: Set of literals.
        """
        lits = set()
        if self.assigned:
            lits.add(self.literal)
        elif self.assigned is False:
            lits.add(-self.literal)
        for stmt in self.statements:
            lits.update(stmt.literals)
        return lits

    def convert_vars(self, vars: list[clingo.Symbol], input: bool = True) -> list[clingo.Symbol]:
        """
        Convert the name of the variable from e.g. x to execution_input(fname, x) or execution_output(fname, x).

        Args:
            vars: List of variable symbols.
            input: If True, convert to input; otherwise, output.

        Returns:
            list[clingo.Symbol]: Converted variable symbols.
        """
        converted: list[clingo.Symbol] = []
        for var in vars:
            converted.append(self.convert_var(var, input=input))
        return converted

    def convert_var(self, var: clingo.Symbol | str, input: bool = True) -> clingo.Symbol:
        """
        Convert a variable to an execution input or output symbol.

        Args:
            var: Variable symbol or string.
            input: If True, convert to input; otherwise, output.

        Returns:
            clingo.Symbol: Converted symbol.
        """
        exec_name: str = EXECUTION_INPUT if input else EXECUTION_OUTPUT

        if isinstance(var, clingo.Symbol):
            var_func = var
        else:
            var_func = clingo.String(var)

        v = clingo.Function(exec_name, [self.func_name, var_func])
        return v

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the execution and return an EvaluationResult.

        Args:
            evaluations: Current variable evaluations.
            ctl: Clingo propagate control.
            env: Evaluation environment.

        Returns:
            EvaluationResult: Result of the evaluation (CHANGED, NOT_CHANGED, or CONFLICT).
        """
        self.assigned = ctl.assignment.value(self.literal)
        if self.assigned is None:
            return EvaluationResult.NOT_CHANGED

        if self.values != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        if ctl.assignment.is_false(self.literal):
            # if an execution is not run, all its outputs are set to None
            self.values = []
            for c_out_var in self.converted_out_vars:
                self.values.append((c_out_var, None))
            self.decision_level = ctl.assignment.decision_level
            return EvaluationResult.CHANGED

        for var in self.converted_in_vars:
            if var not in evaluations and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.values == ValueStatus.NOT_SET
                return EvaluationResult.NOT_CHANGED

        # TODO: see if we can improve this code.
        # There is a lot of copying of the evaluations dictionary!
        evals = {}
        for c_var, var in zip(self.converted_in_vars, self.in_vars):
            evals[var] = evaluations[c_var]

        final_evals = dict()
        for stmt in self.statements:
            __evals = evals.copy()
            result = stmt.evaluate(__evals, ctl, env)
            if result == EvaluationResult.CONFLICT:
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.CONFLICT
            elif result == EvaluationResult.CHANGED:
                final_evals = __evals.copy()

        # check if multiple statements were run
        # if so, take the last one run and add warning
        # TODO: check if this is fine or better return conflict?
        if sum([1 for stmt in self.statements if stmt.assigned]) > 1:
            self.errors.append(
                warning.Warning(
                    warning.Variable(warning.VariableWarning.multipleAssignments),  # ty:ignore[unresolved-attribute]
                    (self.func_name,),
                    "Multiple statements in the same execution were run! Only the last one will be used!",
                )
            )

        self.decision_level = ctl.assignment.decision_level

        self.values: list[tuple[clingo.Symbol, Any]] = []
        for c_out_var, out_var in zip(self.converted_out_vars, self.out_vars):
            if out_var not in final_evals:
                self.values.append((c_out_var, None))
            else:
                self.values.append((c_out_var, final_evals[out_var]))

        return EvaluationResult.CHANGED

    def get_value(self) -> ValueStatus | list[tuple[clingo.Symbol, Any]]:
        """
        Get the current values of the execution outputs.

        Returns:
            ValueStatus | list[tuple[clingo.Symbol, Any]]: Output values or NOT_SET.
        """
        return self.values

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from the execution and its statements.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        errors = self.errors.copy()
        for stmt in self.statements:
            errors.extend(stmt.get_errors())
        return errors

    def add_run_literal(self, lit: int):
        """
        Set the literal for the execution run atom.

        Args:
            lit: Literal value.
        """
        self.literal = lit

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all input variables for the execution.

        Returns:
            set[clingo.Symbol]: Set of input variable symbols.
        """
        return set(self.converted_in_vars)

    def reset(self, dl: int):
        """
        Reset the execution and its statements based on the decision level.

        Args:
            dl: Decision level threshold.
        """
        for stmt in self.statements:
            stmt.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.errors = []
            self.values = ValueStatus.NOT_SET

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        """
        Add the execution's output values to the provided dictionary.

        Args:
            d: Dictionary to update.
        """
        value = self.get_value()

        if value == ValueStatus.NOT_SET:
            return

        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            for out_var in self.converted_out_vars:
                d[FALSE_ASSIGNMENTS].append(out_var)  # type: ignore
        else:
            for out_var, val in value:
                d[out_var] = val

    def __hash__(self) -> int:
        return hash((self.func_name, tuple(self.statements), tuple(self.in_vars), tuple(self.out_vars)))

    def __repr__(self) -> str:
        return f"Execution({self.name}, {self.func_name}, {self.statements})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Execution):
            return False
        return (
            self.func_name == other.func_name
            and self.statements == other.statements
            and self.in_vars == other.in_vars
            and self.out_vars == other.out_vars
        )


class ExecutionStatement:
    """
    Represents a possible statement that an execution can run.

    Attributes:
        statement: The statement to execute.
        literal: Associated literal.
        value: Current value of the statement.
        errors: List of warnings or errors encountered during evaluation.
        assigned: Truth value of the statement.
        decision_level: Decision level at which the value was set.
    """

    def __init__(self, stmt: statement.Stmt, literal: int):
        """
        Initialize an ExecutionStatement.

        Args:
            stmt: Statement to execute.
            literal: Associated literal.
        """
        self.statement = stmt
        self.literal = literal
        self.value: ValueStatus | list[tuple[clingo.Symbol, Any]] = ValueStatus.NOT_SET
        self.errors: propagator_warning_t = []
        self.assigned: bool | None = None
        self.decision_level: int = DEFAULT_DECISION_LEVEL

    @property
    def literals(self) -> set[int]:
        """
        Get the literal(s) associated with this statement.

        Returns:
            set[int]: Set of literals.
        """
        if self.assigned is None:
            return set()
        elif self.assigned:
            return {self.literal}
        else:
            return {-self.literal}

    def get_value(self) -> ValueStatus | list[tuple[clingo.Symbol, Any]]:
        """
        Get the current value of the statement.

        Returns:
            ValueStatus | list[tuple[clingo.Symbol, Any]]: Value or NOT_SET.
        """
        return self.value

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from the statement evaluation.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        return self.errors

    def reset(self, dl: int):
        """
        Reset the statement based on the decision level.

        Args:
            dl: Decision level threshold.
        """
        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.errors = []
            self.value = ValueStatus.NOT_SET
            self.assigned = None

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the execution statements and return an EvaluationResult.

        Args:
            evaluations: Current variable evaluations.
            ctl: Clingo propagate control.
            env: Evaluation environment.

        Returns:
            EvaluationResult: Result of the evaluation (CHANGED, NOT_CHANGED, or CONFLICT).
        """
        self.assigned = ctl.assignment.value(self.literal)
        if self.assigned is None:
            return EvaluationResult.NOT_CHANGED

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        if ctl.assignment.is_false(self.literal):
            # if a particular statement is not executed,
            # then the value of this statement is just a false assignment
            # TODO: see what to return here, change or not?
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            self.decision_level = ctl.assignment.decision_level
            return EvaluationResult.NOT_CHANGED

        try:
            errors = evaluator.evaluate_stmt(self.statement, env, evaluations)
            self.decision_level: int = ctl.assignment.decision_level
            for error, msg in errors:
                self.errors.append(warning.Warning(error, (), repr(msg)))
        except solver_environment.FailIntegrityExn:
            self.decision_level: int = ctl.assignment.decision_level
            return EvaluationResult.CONFLICT

        return EvaluationResult.CHANGED


def make_dict_from_variables(
    variables: Iterable[VariableType],
) -> dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]:
    """Build a plain Python dictionary from a collection of variables.

    The resulting dictionary maps each variable symbol to its evaluated value.
    Variables that are assigned false are listed under the `FALSE_ASSIGNMENTS` key.

    Args:
        variables: Iterable of variables to export. Variables must implement the `add_self_to_dict` method!

    Returns:
        dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]: Dictionary of variable values.
    """
    result: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]] = {FALSE_ASSIGNMENTS: []}  # type: ignore
    for var in variables:
        var.add_self_to_dict(result)

    return result
