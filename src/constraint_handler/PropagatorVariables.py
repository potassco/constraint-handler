from __future__ import annotations

import sys
from abc import abstractmethod
from collections.abc import Iterable
from itertools import product
from typing import Any, Literal, Protocol, runtime_checkable

import clingo

from constraint_handler import evaluator, multimap, myClorm
from constraint_handler.PropagatorConstants import (
    DEFAULT_DECISION_LEVEL,
    EvaluationResult,
    ValueStatus,
    evaluations_type,
    propagator_warning_t,
)
from constraint_handler.schemas import expression, warning


def create_bad_value_warning(variable: VariableType | EvaluateVariable) -> warning.Warning | None:

    if not (
        variable.get_value() == expression.Bad.bad  # ty:ignore[unresolved-attribute]
        or (
            isinstance(variable.get_value(), frozenset) and expression.Bad.bad in variable.get_value()
        )  # ty:ignore[unresolved-attribute]
        or (
            isinstance(variable.get_value(), dict)
            and (
                expression.Bad.bad in variable.get_value().values() or expression.Bad.bad in variable.get_value().keys()
            )  # ty:ignore[unresolved-attribute]
        )
    ):
        return None

    return warning.Warning(
        warning.Variable(warning.VariableWarning.badValue),  # ty:ignore[unresolved-attribute]
        (),
        variable.var,
    )


def is_evaluation_possible(var: VariableType | VariableValue) -> bool:
    """
    Check whether evaluation is possible for this variable
    by checking the count of evaluated expressions against the total expressions count.

    Args:
        var: The variable or variable value to check for evaluation possibility.

    Returns:
        bool: True if evaluation is possible, False otherwise.
    """
    if isinstance(var, VariableType):
        if var.expressions_evaluated_counter > var.expressions_count:
            raise RuntimeError("Expressions evaluated counter exceeds expressions count.")
        # print(
        #     f"Assesing evaluation possibility for variable: {var} with expressions evaluated counter: {var.expressions_evaluated_counter} and expressions count: {var.expressions_count}"
        # )
        return var.expressions_evaluated_counter == var.expressions_count
    elif isinstance(var, VariableValue):
        if var.vars_counter > var.vars_count:
            raise RuntimeError("Vars counter exceeds vars count.")
        # print(
        #     f"Assesing evaluation possibility for variable value: {var} with vars counter: {var.vars_counter} and vars count: {var.vars_count}"
        # )
        return var.vars_counter == var.vars_count

    raise TypeError(f"Unsupported variable type for evaluation possible check. {type(var)}")


@runtime_checkable
class VariableType(Protocol):
    """
    Protocol for variable types used in the propagator. Defines the required interface for variables.
    """

    name: str
    expressions_count: int
    expressions_evaluated_counter: int

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

    @property
    @abstractmethod
    def active_literals(self) -> set[int]: ...

    @property
    @abstractmethod
    def expressions(self) -> set[VariableValue]: ...

    @abstractmethod
    def has_domain(self) -> bool: ...

    @abstractmethod
    def has_unassigned(self) -> bool: ...

    @abstractmethod
    def get_value(self) -> Any: ...

    @abstractmethod
    def reset(self, dl: int) -> bool: ...

    @abstractmethod
    def get_errors(self) -> propagator_warning_t: ...

    @abstractmethod
    def vars(self) -> set[clingo.Symbol]: ...

    @abstractmethod
    def evaluate(
        self,
        ctl: clingo.PropagateControl,
    ) -> EvaluationResult: ...

    @abstractmethod
    def infer(self) -> set[int]: ...


class VariableManager:
    """
    Manages variables in the propagator. This includes storing variables, retrieving them by name and type,
    and resetting them based on decision levels.

    Attributes:
        variables: Dictionary mapping variable names to VariableType instances.
    """

    def __init__(self) -> None:
        self.variables: dict[clingo.Symbol, dict[VariableTypeNames, VariableType]] = {}
        self.user_variable_names: set[clingo.Symbol] = set()
        self.expr2var: dict[VariableValue, list[VariableType]] = {}
        self.var2expr: dict[clingo.Symbol, set[VariableValue]] = {}
        self.lit2expr: dict[int, set[VariableValue]] = {}
        self.literal2var: dict[int, list[VariableType]] = {}
        self.var_ranks: dict[clingo.Symbol, int] = {}
        self.var_ranks_expr: dict[VariableValue, int] = {}
        self.value_registry = VariableValueRegistry()

    def get_variable_value(self, expr: expression.Expr, literal: int) -> VariableValue:
        """
        Intern a value and index it by its solver literal.

        Args:
            expr: Expression object.
            literal: Solver literal.
        Returns:
            VariableValue: Interned expression value.
        """
        value = self.value_registry.get(expr, literal)
        self.add_literal_expr(literal, value)
        # maybe doing this is ineficient and it is better the way it was before
        # of doing this once all expressions are interned.
        for var in value.vars():
            self.add_var_expr(var, value)
        return value

    def get_all_expressions(self) -> list[VariableValue]:
        """
        Return a snapshot of all interned expression values.
        Returns:
            list[VariableValue]: All interned expression values.

        """
        return self.value_registry.get_all()

    def add_literal_var(self, literal: int, variable: VariableType) -> None:
        """
        Associate a variable with the positive form of a solver literal.

        Args:
            literal: Solver literal.
            variable: Variable to associate with the literal.
        """
        self.literal2var.setdefault(abs(literal), []).append(variable)

    def get_literal_vars(self, literal: int) -> list[VariableType]:
        """
        Get variables associated with a solver literal, regardless of sign.

        Args:
            literal: Solver literal.
        Returns:
            list[VariableType]: Associated variables.
        """
        return self.literal2var.get(abs(literal), [])

    def delete_literal_var(self, literal: int, variable: VariableType) -> bool:
        """
        Remove a literal-variable association, returning whether it existed.

        Args:
            literal: Solver literal.
            variable: Variable to disassociate from the literal.
        Returns:
            bool: True if the association existed and was removed, False otherwise.
        """
        key = abs(literal)
        variables = self.literal2var.get(key)
        if variables is None:
            return False

        try:
            variables.remove(variable)
        except ValueError:
            return False

        if not variables:
            del self.literal2var[key]
        return True

    def add_expr_owner(self, value: VariableValue, variable: VariableType) -> None:
        """
        Associate an interned value with its owning variable.

        Args:
            value: Interned expression value.
            variable: Owning variable.
        """
        owners = self.expr2var.setdefault(value, [])
        if not any(owner is variable for owner in owners):
            owners.append(variable)

    def get_expr_owners(self, expr: VariableValue) -> list[VariableType]:
        """
        Get the variables owning an expression value, or an empty list.

        Args:
            expr: Expression value.
        Returns:
            list[VariableType]: Owning variables.
        """
        return self.expr2var.get(expr, [])

    def remove_expr_owner(self, expr: VariableValue, variable: VariableType) -> None:
        """
        Remove a variable from the owners of an expression value, if present.

        Args:
            expr: Expression value.
            variable: Owner to remove.
        """
        owners = self.expr2var.get(expr)
        if owners is not None and variable in owners:
            owners.remove(variable)

    def add_var_expr(self, var: clingo.Symbol, expr: VariableValue) -> None:
        """
        Record that an expression value depends on a variable symbol.

        Args:
            var: Variable symbol used by the expression.
            expr: Expression value using the variable.
        """
        self.var2expr.setdefault(var, set()).add(expr)

    def get_var_exprs(self, var: clingo.Symbol) -> set[VariableValue]:
        """
        Get the expression values that depend on a variable symbol.

        Args:
            var: Variable symbol.
        Returns:
            set[VariableValue]: Dependent expression values.
        """
        return self.var2expr.get(var, set())

    def add_literal_expr(self, literal: int, value: VariableValue) -> None:
        """
        Associate a value with the positive form of a solver literal.

        Args:
            literal: Solver literal.
            value: Expression value to associate with the literal.
        """
        self.lit2expr.setdefault(abs(literal), set()).add(value)

    def get_literal_exprs(self, literal: int) -> set[VariableValue]:
        """
        Get values associated with a solver literal, regardless of sign.

        Args:
            literal: Solver literal.
        Returns:
            set[VariableValue]: Associated expression values.
        """
        return self.lit2expr.get(abs(literal), set())

    def add_user_variable_name(self, name: clingo.Symbol) -> None:
        """
        Add a variable name to the set of user variable names.

        Args:
            name: The variable name to add.
        """
        self.user_variable_names.add(name)

    def add_variable(self, name: clingo.Symbol, variable: VariableType) -> None:
        """
        Add a variable to the manager.
        We assume that this is called only once for a given VariableType

        Args:
            name: The name of the variable to add.
            variable: The VariableType instance to add.
        """
        if name not in self.variables:
            self.variables[name] = {}
        self.variables[name][variable.__class__.__name__] = variable

    def is_user_variable(self, name: clingo.Symbol) -> bool:
        """
        Check if a variable name is a user variable.

        Args:
            name: The variable name to check.
        Returns:
            bool: True if the variable name is a user variable, False otherwise.
        """
        return name in self.user_variable_names

    def get_variables(self) -> Iterable[VariableType]:
        """
        Get all variables managed by this VariableManager.
        Returns:
            Iterable[VariableType]: An iterable of all VariableType instances.
        """

        for var_dict in self.variables.values():
            yield from var_dict.values()

    def get_variables_by_type(self, var_type: VariableTypeNames) -> Iterable[VariableType]:
        """
        Get all variables of a specific type.

        Args:
            var_type: The type of variables to retrieve.
        Returns:
            Iterable[VariableType]: An iterable of VariableType instances of the specified type.
        """
        for var_dict in self.variables.values():
            if var_type in var_dict:
                yield var_dict[var_type]

    def get_variable(self, name: clingo.Symbol, var_type: VariableTypeNames) -> VariableType:
        """
        Get a variable by name and type.

        Args:
            name: The name of the variable to retrieve.
            var_type: The type of the variable to retrieve.
        Returns:
            The VariableType instance if found.
        Raises:
            KeyError: If the variable with the specified name and type does not exist.
        """

        if name not in self.variables or var_type not in self.variables[name]:
            raise KeyError(f"Variable with name {name} and type {var_type} does not exist.")
        return self.variables[name][var_type]

    def has_var_type(self, name: clingo.Symbol, var_type: VariableTypeNames) -> bool:
        """
        Check if a variable of a specific type exists for a given name.

        Args:
            name: The name of the variable to check.
            var_type: The type of the variable to check.
        Returns:
            bool: True if the variable of the specified type exists, False otherwise.
        """
        return name in self.variables and var_type in self.variables[name]

    def delete_variable(self, name: clingo.Symbol) -> None:
        """
        Delete a variable by name.

        Args:
            name: The name of the variable to delete.
        Raises:
            KeyError: If the variable with the specified name does not exist.
        """
        if name not in self.variables:
            raise KeyError(f"Variable with name {name} does not exist. Can not delete")
        del self.variables[name]

    def get_dependencies(self, name: clingo.Symbol) -> set[clingo.Symbol]:
        """
        Get the dependencies of a variable by name.

        Args:
            name: The name of the variable to retrieve dependencies for.
        Returns:
            set[clingo.Symbol]: A set of variable names that are dependencies of the specified variable.
        """
        if name not in self.variables:
            raise KeyError(f"Variable with name {name} does not exist. Can not get dependencies")
        deps = set()
        for var in self.variables[name].values():
            deps.update(var.vars())
        return deps

    def items(self) -> Iterable[tuple[clingo.Symbol, dict[VariableTypeNames, VariableType]]]:
        """
        Get all variable items as (name, variable_dict) pairs.

        Returns:
            Iterable[tuple[clingo.Symbol, dict[VariableTypeNames, VariableType]]]: An iterable of (name, variable_dict) pairs.
        """
        return self.variables.items()

    def keys(self) -> Iterable[clingo.Symbol]:
        """
        Get all variable names.

        Returns:
            Iterable[clingo.Symbol]: An iterable of variable names.
        """
        return self.variables.keys()

    def values(self) -> Iterable[dict[VariableTypeNames, VariableType]]:
        """
        Get all variable dictionaries.

        Returns:
            Iterable[dict[VariableTypeNames, VariableType]]: An iterable of variable dictionaries.
        """
        return self.variables.values()

    def remove(self, variable: clingo.Symbol) -> None:
        """
        Remove a variable by name.

        Args:
            variable: The name of the variable to remove.
        Raises:
            KeyError: If the variable with the specified name does not exist.
        """
        if variable not in self.variables:
            raise KeyError(f"Variable with name {variable} does not exist. Can not delete")
        del self.variables[variable]

    def compute_ranks(self) -> None:
        """
        Assign ranks to variables based on the ranks of their dependencies,
        then to interned expressions based on the variables they use.

        Variables whose dependencies can never be satisfied get rank -1,
        as do expressions that use an unknown variable.
        """
        # loop over vars and get the ones without deps, those have rank 0
        # loop again and get vars with satisfied deps based on known ranks
        # those get rank +1
        known_vars: set[clingo.Symbol] = set()
        changed = True
        rank = 0
        while changed:
            changed = False
            vars_this_loop: set[clingo.Symbol] = set()
            for var in self.variables:
                if var in known_vars:
                    continue
                if self.get_dependencies(var).issubset(known_vars):
                    self.var_ranks[var] = rank
                    changed = True
                    vars_this_loop.add(var)

            known_vars.update(vars_this_loop)
            rank += 1

        for v in set(self.variables) - known_vars:
            self.var_ranks[v] = -1

        for expr in self.get_all_expressions():
            try:
                self.var_ranks_expr[expr] = max((self.var_ranks[var] + 1 for var in expr.vars()), default=0)
            except KeyError:
                self.var_ranks_expr[expr] = -1

    def get_var_rank(self, var: clingo.Symbol) -> int:
        """
        Get the rank of a variable symbol.

        Args:
            var: Variable symbol.
        Raises:
            KeyError: If ranks were not computed for the variable.
        """
        return self.var_ranks[var]

    def get_expr_rank(self, expr: VariableValue) -> int:
        """
        Get the rank of an expression value.

        Args:
            expr: Expression value.
        Raises:
            KeyError: If ranks were not computed for the expression.
        """
        return self.var_ranks_expr[expr]

    def __getitem__(self, name: clingo.Symbol) -> dict[VariableTypeNames, VariableType]:
        return self.variables[name]

    def __contains__(self, name: clingo.Symbol) -> bool:
        return name in self.variables

    def __len__(self) -> int:
        return len(self.variables)


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

    def __init__(self, expr: expression.Expr, lit: int) -> None:
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

        self.vars_count: int = len(self.vars())
        self.vars_counter = 0

        self.errors: propagator_warning_t = []

    def evaluate(self, evaluations: Evaluations, ctl: clingo.PropagateControl, env: dict[Any, Any]) -> bool:
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
            # If a variable that exists is not yet assigned(A value or False assignment), then we cannot evaluate yet
            if not evaluations.var_usable(var):
                # can't evaluate yet
                # value should not be set yet
                assert self.value == ValueStatus.NOT_SET
                return False

        self.value, errors = evaluator.evaluate_expr(self.expr, env, evaluations.evaluations)

        if isinstance(self.value, set):
            self.value = frozenset(self.value)
        elif isinstance(self.value, (multimap.Multimap, dict)):
            pass
        else:
            res, err = evaluator.reducedExpr(self.value)
            if res == expression.Bad.bad:
                self.value = expression.Bad.bad
                for error, msg in err:
                    self.errors.append(warning.Warning(error, (), repr(msg)))

        for error, msg in errors:
            self.errors.append(warning.Warning(error, (), repr(msg)))

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

    def reset(self, dl: int) -> bool:
        """
        Reset based on decision level.

        Args:
            dl: Decision level threshold.

        Returns:
            bool: True if the value was reset; False otherwise.
        """
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.assigned = None
            self.errors = []
            return True
        return False

    @property
    def literals(self) -> set[int]:
        """
        Return the literal associated with this expression

        Returns:
            set[int]: A singleton set containing the literal
        """
        return {self.literal}

    @property
    def active_literals(self) -> set[int]:
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableValue):
            return False
        return self.expr == other.expr and self.literal == other.literal

    def __hash__(self) -> int:
        return hash((str(self.expr), self.literal))

    def __str__(self) -> str:
        return f"VariableValue({self.expr}, {self.value}, {self.literal})"

    def __repr__(self) -> str:
        return f"VariableValue({self.expr}, {self.value}, {self.literal})"


class VariableValueRegistry:
    """Intern VariableValue instances."""

    def __init__(self) -> None:
        self.values: dict[tuple[str, int], VariableValue] = {}

    def get(self, expr: expression.Expr, lit: int) -> VariableValue:
        key = (str(expr), lit)
        value = self.values.get(key)
        if value is None:
            value = VariableValue(expr, lit)
            self.values[key] = value

        return value

    def get_all(self) -> list[VariableValue]:
        """
        Return a snapshot of all interned values.

        Returns:
            list[VariableValue]: A list of all interned VariableValue instances.
        """
        return list(self.values.values())

    def delete(self, value: VariableValue) -> bool:
        """
        Remove the given instance, returning whether it was registered.

        Args:
            value: The VariableValue instance to remove.

        Returns:
            bool: True if the instance was registered and removed; False otherwise.
        """
        key = (str(value.expr), value.literal)
        if self.values.get(key) is not value:
            return False

        del self.values[key]
        return True


class EvaluateVariable:
    """
    Represents an evaluate atom defined by an operator and arguments of the operator.

    Attributes:
        ref: User-facing reference.
        value: The current value of the evaluation.
        literal: The associated literal.
        errors: List of warnings or errors encountered during evaluation.
    """

    def __init__(self, ref: expression.constant, expr: expression.Expr, literal: int = -1) -> None:
        """
        Initialize an EvaluateVariable.

        Args:
            ref: User-facing reference.
            expr: Expression to evaluate.
            literal: Literal controlling whether this operation is active.
        """
        self.ref: expression.constant = ref
        self.expr: expression.Expr = expr
        self.value: Any = ValueStatus.NOT_SET
        self.literal: int = literal

        self.errors: propagator_warning_t = []

    def evaluate(self, evaluations: Evaluations, ctl: clingo.PropagateControl, env: dict[Any, Any]) -> bool:
        """
        Evaluate the expression

        Args:
            evaluations: Current variable evaluations.
            ctl: PropagateControl for checking literal assignments and decision levels.
            env: Environment for evaluation.

        Returns:
            bool: True if the value has changed, False otherwise.
        """
        if ctl.assignment.value(self.literal) is None:
            return False

        if ctl.assignment.is_false(self.literal):
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            return False

        value, errors = evaluator.evaluate_expr(self.expr, env, evaluations.evaluations)
        self.value = value
        for error, msg in errors:
            self.errors.append(warning.Warning(error, (), repr(msg)))

        bad_value_warning = create_bad_value_warning(self)
        if bad_value_warning is not None:
            self.errors.append(bad_value_warning)

        return True

    @property
    def var(self) -> clingo.Symbol:
        """
        Return a symbolic representation of this evaluation variable.

        Returns:
            clingo.Symbol: A symbolic representation of this variable.
        """
        return myClorm.pytocl(self.expr)

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EvaluateVariable):
            return False
        return self.ref == other.ref and self.expr == other.expr and self.literal == other.literal

    def __hash__(self) -> int:
        return hash((str(self.ref), str(self.expr), self.literal))

    def __str__(self) -> str:
        return f"EvaluateVariable({self.ref}, {self.expr})"

    def __repr__(self) -> str:
        return self.__str__()


class SharedValue:
    """
    Represents a shared value that is used by other parts of the constraint handler.
    """

    def __init__(self, expr: expression.Expr, literal: int = -1) -> None:
        """
        Initialize a SharedValue.

        Args:
            expr: The expression associated with this shared value.
            literal: Literal controlling whether this operation is active.
        """
        self.expr: expression.Expr = expr
        self.value: Any = ValueStatus.NOT_SET
        self.literal: int = literal

        self.errors: propagator_warning_t = []

    def evaluate(self, evaluations: Evaluations, ctl: clingo.PropagateControl, env: dict[Any, Any]) -> bool:
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
        value, errors = evaluator.evaluate_expr(self.expr, env, evaluations.evaluations)
        self.value = value
        for error, msg in errors:
            self.errors.append(warning.Warning(error, (), repr(msg)))

        bad_value_warning = create_bad_value_warning(self)
        if bad_value_warning is not None:
            self.errors.append(bad_value_warning)

        return True

    @property
    def var(self) -> clingo.Symbol:
        """
        Return a symbolic representation of this evaluation variable.

        Returns:
            clingo.Symbol: A symbolic representation of this variable.
        """
        return myClorm.pytocl(self.expr)

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SharedValue):
            return False
        return self.expr == other.expr and self.literal == other.literal

    def __hash__(self) -> int:
        return hash((str(self.expr), self.literal))

    def __str__(self) -> str:
        return f"SharedValue({self.expr})"

    def __repr__(self) -> str:
        return self.__str__()


class BoolEvaluateVariable:
    """
    Represents a boolean evaluation variable, which is a special case of EvaluateVariable that is expected to evaluate to a boolean value.
    This class can be used for variables that are expected to represent conditions or constraints that must hold.

    Attributes:
        name: Name of the variable.
        expression: The VariableValue instance being evaluated.
    """

    __c = 0
    __var = "__bool_evaluate__"

    def __init__(
        self,
        name: str,
        expression_value: VariableValue,
        true_lit: int,
        false_lit: int,
        bad_lit: int,
    ) -> None:
        """
        Initialize a BoolEvaluateVariable.

        Args:
            name: Name of the variable.
            expression_value: Interned expression to evaluate, expected to yield a boolean value.
            true_lit: Literal representing the true value of the variable.
            false_lit: Literal representing the false value of the variable.
            bad_lit: Literal representing a bad value of the variable.
        """
        self.name: str = name
        self.expression: VariableValue = expression_value
        self.value_lits = {True: true_lit, False: false_lit, expression.Bad.bad: bad_lit}
        self.value = None
        self.var = clingo.Function(BoolEvaluateVariable.__var, [clingo.Number(BoolEvaluateVariable.__c)])
        BoolEvaluateVariable.__c += 1

        self.expressions_count: int = 1
        self.expressions_evaluated_counter: int = 0

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return the set of VariableValue instances associated with this variable.

        Returns:
            set[VariableValue]: Set containing the VariableValue of this boolean evaluation variable.
        """
        return {self.expression}

    @property
    def parents(self) -> list[VariableType]:
        """
        Return parent variables.

        Returns:
            list[VariableType]: Empty list (bool evaluate variables have no parents).
        """
        return []

    def has_domain(self) -> bool:
        """
        Return whether the variable has a domain.

        Returns:
            bool: Always True for BoolEvaluateVariable.
        """
        return True

    @property
    def literals(self) -> set[int]:
        """
        Return all literals associated with this boolean evaluation variable.

        Returns:
            set[int]: Set of all literals (true, false, and bad) for this variable and the literal of the expression.
        """
        return set(self.value_lits.values()).union({self.expression.literal})

    @property
    def active_literals(self) -> set[int]:
        """
        Return signed literals that give the current value of the boolean evaluation variable.

        Returns:
            set[int]: Set of signed literals.
        """

        return self.expression.active_literals

    def evaluate(
        self,
        ctl: clingo.PropagateControl,
    ) -> EvaluationResult:
        """
        Evaluate the expression and return an EvaluationResult.

        Args:
            ctl: PropagateControl

        Returns:
            EvaluationResult: Result of the evaluation, indicating whether the value changed or if an inference should be made.
        """
        # changed: Unknown = self.expression.evaluate(evaluations, ctl, env)
        if self.get_value() is not ValueStatus.ASSIGNMENT_IS_FALSE:
            # if we got a value, we can infer the corresponding literal
            return EvaluationResult.INFER

        return EvaluationResult.NOT_CHANGED

    def infer(self) -> set[int]:
        """
        Infer the literal corresponding to the current value.

        Returns:
            set[int]: A singleton set containing the signed literal if assigned; otherwise empty.
                      Note that literal is flipped so that the nogood infers the correct value.
        """
        value = self.get_value()
        if value in self.value_lits:
            return {-self.value_lits[value]}
        return set()

    def get_value(self) -> ValueStatus | bool | expression.Bad:
        """
        Return the current value of the boolean evaluation variable.

        Returns:
            ValueStatus | bool | expression.Bad: Current value, or NOT_SET.
        """
        return self.expression.value

    def has_unassigned(self) -> bool:
        """
        Check whether the boolean evaluation variable is unassigned.

        Returns:
            bool: True if the value is NOT_SET.
        """
        return self.get_value() == ValueStatus.NOT_SET

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect variables referenced by the boolean evaluation expression.

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
        errors = self.expression.get_errors()
        bad_value_warning = create_bad_value_warning(self)
        if bad_value_warning is not None:
            errors.append(bad_value_warning)
        return errors

    def reset(self, dl: int) -> bool:
        """
        Reset based on the decision level.

        Args:
            dl: Decision level threshold.
        Returns:
            bool: False since there is nothing to reset
        """
        # self.expression.reset(dl)
        return False

    @property
    def decision_level(self) -> int:
        """
        Return the decision level at which the value was set.

        Returns:
            int: Decision level of the variable.
        """
        return self.expression.decision_level

    def __eq__(self, other) -> bool:
        if not isinstance(other, Variable):
            return False
        return self.var == other.var and self.expression == other.expression

    def __hash__(self) -> int:
        return hash((self.var, self.expression))

    def __str__(self) -> str:
        return f"BoolEvaluateVariable({self.name}, {self.var}, {self.expression})"

    def __repr__(self) -> str:
        return f"BoolEvaluateVariable({self.name}, {self.var}, {self.expression})"


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
        is_user_variable: Whether this variable is defined by the user or is an internal variable
    """

    def __init__(self, name: str, var: clingo.Symbol, is_user_variable: bool = False) -> None:
        """
        Initialize a Variable.

        Args:
            name: Name for the variable.
            var: Clingo symbol representing this variable.
            is_user_variable: Whether this variable is defined by the user or is an internal variable.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: set[VariableValue] = set()
        self.value: Any = ValueStatus.NOT_SET
        self.parents: list[VariableType] = []
        self.is_user_variable: bool = is_user_variable
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.expressions_count: int = 0
        self.expressions_evaluated_counter: int = 0

        # literals for atoms that can define a domain
        # (variable_define, variable_declare, variable_optinal)
        self.domain_literals: set[int] = set()

        self.errors: propagator_warning_t = []

    def add_value(self, value: VariableValue, domain_lit: int) -> None:
        """
        Add a possible value expression for this variable.

        Args:
            value: Interned expression representing a candidate value.
            domain_lit: Literal indicating the truth value of the domain/declaration context.
        """
        if value in self.expressions:
            return
        self.expressions.add(value)
        self.expressions_count += 1
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
        Bad value warnings are filtered out for non user variables.

        Returns:
            propagator_warning_t: List of warnings.
        """
        errors: propagator_warning_t = []
        for var_value in self.expressions:
            errors.extend(var_value.get_errors())
            if self.is_user_variable:
                bad_value_warning = create_bad_value_warning(self)
                if bad_value_warning is not None:
                    errors.append(bad_value_warning)
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
        self,
        ctl: clingo.PropagateControl,
    ) -> EvaluationResult:
        """
        Evaluate the expression and return an EvaluationResult.
        Args:
            ctl: PropagateControl object for interacting with the solver.

        Returns:
            EvaluationResult: Result of the evaluation.
        """

        if self.value != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        val = self.get_values()
        if len(val) > 1:
            # multiple values assigned to the same variable
            # this is True even if the same value is assigned multiple times
            self.decision_level = ctl.assignment.decision_level
            self.value = ValueStatus.ASSIGNMENT_IS_FALSE
            return EvaluationResult.CONFLICT
        elif len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                val = [ValueStatus.NOT_SET]
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.NOT_CHANGED

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

    def get_literals(self, active: bool) -> set[int]:
        """
        Return the literal associated with this expression

        Args:
            active: Whether to return active (signed) literals that give this variable its value or all literals.

        Returns:
            set[int]: A singleton set containing the literal
        """
        lits: set[int] = set()
        for value in self.expressions:
            if active:
                lits.update(value.active_literals)
            else:
                lits.update(value.literals)
        return lits

    @property
    def literals(self) -> set[int]:
        """
        Return the literal associated with this expression

        Returns:
            set[int]: A singleton set containing the literal
        """
        return self.get_literals(active=False)

    @property
    def active_literals(self) -> set[int]:
        """
        Return signed literals implied by all candidate values.

        Returns:
            set[int]: Set of signed literals.
        """
        return self.get_literals(active=True)

    def reset(self, dl: int) -> bool:
        """
        Reset based on decision level.

        Args:
            dl: Decision level threshold.

        Returns:
            bool: True if the variable was reset, False otherwise.
        """
        # for value in self.expressions:
        #     value.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []
            return True
        return False

    def infer(self) -> set[int]:
        """
        Currently this returns an empty set as it does not support any inferences.
        This is here for compatibility with the VariableType protocol.

        Returns:
            set[int]: Empty set (no inferences).
        """
        return set()

    def __eq__(self, other: object) -> bool:
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

        # Set of pairs (value, condition_value) representing possible values and their conditions.
        # A None condition is treated as always true, meaning the value is always added to the set.
        self.expressions_pairs: set[tuple[VariableValue, VariableValue | None]] = set()

    def has_domain(self) -> bool:
        """
        Return whether at least one value expression is present.

        Returns:
            bool: True if any value expression exists.
        """
        return len(self.expressions_pairs) > 0

    def add_value(self, value: VariableValue, condition_value: VariableValue | None = None) -> None:
        """
        Add a candidate value to the set.

        Args:
            value: Interned expression for a set element.
        """
        self.expressions_pairs.add((value, condition_value))

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings collected while evaluating set elements.

        Returns:
            propagator_warning_t: List of warnings.
        """
        errors: propagator_warning_t = []
        for var_value, condition_value in self.expressions_pairs:
            errors.extend(var_value.get_errors())
            if condition_value is not None:
                errors.extend(condition_value.get_errors())
        return errors

    def get_literals(self, active: bool) -> set[int]:
        """
        Return the literals associated with the set elements.

        Args:
            active: Whether to return active (signed) literals that give this variable its value or all literals.

        Returns:
            set[int]: Set of literals.
        """
        lits: set[int] = set()
        for value, condition_value in self.expressions_pairs:
            if active:
                lits.update(value.active_literals)
                if condition_value is not None:
                    lits.update(condition_value.active_literals)
            else:
                lits.update(value.literals)
                if condition_value is not None:
                    lits.update(condition_value.literals)
        return lits

    @property
    def literals(self) -> set[int]:
        """
        Return the literal associated with this expression

        Returns:
            set[int]: A singleton set containing the literal
        """
        return self.get_literals(active=False)

    @property
    def active_literals(self) -> set[int]:
        """
        Return signed literals implied by currently evaluated set elements.

        Returns:
            set[int]: Set of signed literals.
        """
        return self.get_literals(active=True)

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return all value expressions in the set variable.

        Returns:
            set[VariableValue]: Set of value expressions.
        """
        exprs = set()
        for value, condition_value in self.expressions_pairs:
            exprs.add(value)
            if condition_value is not None:
                exprs.add(condition_value)
        return exprs

    def get_value(self) -> ValueStatus | frozenset[Any]:
        """
        If there is an unassigned value, return ValueStatus.NOT_SET.
        Otherwise return the set of assigned values.

        Returns:
            ValueStatus | frozenset[Any]: ValueStatus.NOT_SET if any element is unassigned, otherwise a frozenset of assigned values.
        """
        if self.has_unassigned():
            return ValueStatus.NOT_SET
        # Note that we let None be a part of the set!
        # We add the value to the set if condition does not exist
        # (applicable for dicts or other engine set vars that do not have condition for adding) or it is True
        return frozenset(
            arg.value
            for arg, condition_value in self.expressions_pairs
            if arg.value != ValueStatus.ASSIGNMENT_IS_FALSE
            and (condition_value is None or condition_value.value == True)
        )

    def has_unassigned(self) -> bool:
        """
        Check whether any element value is still unassigned.

        Returns:
            bool: True if any element is NOT_SET.
        """
        return any(arg.value == ValueStatus.NOT_SET for arg in self.expressions)

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect variables referenced by all set element expressions.

        Returns:
            set[clingo.Symbol]: Referenced variables.
        """
        vars = set()
        for arg, condition_value in self.expressions_pairs:
            vars.update(arg.vars())
            if condition_value is not None:
                vars.update(condition_value.vars())
        return vars

    def reset(self, dl: int) -> None:
        """
        Reset all element values based on decision level.

        Args:
            dl: Decision level threshold.
        """
        for arg, condition_value in self.expressions_pairs:
            arg.reset(dl)
            if condition_value is not None:
                condition_value.reset(dl)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SetVariableValue):
            return False
        return self.expressions_pairs == other.expressions_pairs

    def __hash__(self) -> int:
        return hash(frozenset(self.expressions_pairs))

    def __str__(self) -> str:
        return f"SetVariableValue({self.expressions_pairs})"

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
        is_user_variable: Whether this variable is defined by the user or is an internal variable
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int, is_user_variable: bool = False) -> None:
        """
        Initialize a SetVariable.

        Args:
            name: Name of the set variable.
            var: Clingo symbol identifying the variable.
            lit: Literal for the set declaration.
            is_user_variable: Whether this variable is defined by the user or is an internal variable.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.set_expressions: SetVariableValue = SetVariableValue()
        self.is_user_variable: bool = is_user_variable

        self.value: ValueStatus | frozenset[Any] = ValueStatus.NOT_SET

        self.literal: int = lit  # this is the literal for the set declaration
        self.assigned: bool | None = None  # Truth value of the set declaration
        self.decision_level: int = DEFAULT_DECISION_LEVEL  # decision level of the set declaration

        self.expressions_count: int = 0
        self.expressions_evaluated_counter: int = 0

        self.parents: list[VariableType] = []

        self.errors: propagator_warning_t = []

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return the set of VariableValue instances representing possible set elements.

        Returns:
            set[VariableValue]: Set of possible element expressions.
        """
        return self.set_expressions.expressions

    def has_domain(self) -> bool:
        """
        Check whether the set has a domain.

        Returns:
            bool: True if at least one value can be assigned.
        """
        return self.set_expressions.has_domain()

    def add_value(self, value: VariableValue, condition_value: VariableValue | None) -> None:
        """
        Add a potential value expression with its associated condition to the set.

        Args:
            value: Interned expression for one possible set element.
            condition_value: Interned expression representing the condition under which the value is added to the set. If None, the value is always added.
        """
        if (value, condition_value) in self.expressions:
            return
        if value not in self.set_expressions.expressions:
            self.expressions_count += 1
        if (
            condition_value is not None
            and value != condition_value
            and condition_value not in self.set_expressions.expressions
        ):
            self.expressions_count += 1
        self.set_expressions.add_value(value, condition_value)

    def get_errors(self) -> propagator_warning_t:
        """
        Return warnings/errors collected during evaluation.
        Bad value warnings are filtered out for non user variables

        Returns:
            propagator_warning_t: Warnings and errors for this set and its elements.
        """
        errors = self.set_expressions.get_errors() + self.errors

        if self.is_user_variable:
            bad_value_warning = create_bad_value_warning(self)
            if bad_value_warning is not None:
                errors.append(bad_value_warning)

        return errors

    def get_literals(self, active: bool) -> set[int]:
        """
        Return the literals associated with the set variable.

        Args:
            active: Whether to return active (signed) literals that give this variable its value or all literals.

        Returns:
            set[int]: Set of literals.
        """
        lits = self.set_expressions.get_literals(active)
        return lits

    @property
    def literals(self) -> set[int]:
        """
        Return the literal associated with this expression

        Returns:
            set[int]: A singleton set containing the literal
        """
        lits = self.get_literals(active=False)
        lits.add(self.literal)
        return lits

    @property
    def active_literals(self) -> set[int]:
        """
        Return literals relevant for this variable's current state.

        Includes literals from all element assignments and, if assigned,
        the set declaration literal.

        Returns:
            set[int]: Set of literals.
        """
        lits = self.get_literals(active=True)
        if self.assigned is not None:
            if self.assigned:
                lits.add(self.literal)
            else:
                lits.add(-self.literal)
        return lits

    def get_value(self) -> ValueStatus | frozenset[Any]:
        """
        See SetVariableValue.get_value

        Returns:
            ValueStatus | frozenset[Any]: The current value of the set variable
        """
        return self.value

    def has_unassigned(self) -> bool:
        """
        Check whether any element expression is still unassigned.

        Returns:
            bool: True if at least one element is unassigned.
        """
        return self.set_expressions.has_unassigned()

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables referenced by this set.

        Returns:
            set[clingo.Symbol]: Variables used in element expressions.
        """
        return self.set_expressions.vars()

    def evaluate(
        self,
        ctl: clingo.PropagateControl,
    ) -> EvaluationResult:
        """
        Evaluate the expression and return an EvaluationResult.

        Args:
            ctl: Clingo propagate control object.

        Returns:
            EvaluationResult: The result of the evaluation, indicating whether the value changed, remained the same, or if there was a conflict.
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
            return EvaluationResult.CHANGED

        if not self.has_unassigned():
            self.value = self.set_expressions.get_value()
            if self.value != ValueStatus.NOT_SET:
                # only update decision level if we have a value
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.CHANGED

        # if nothing changed or the changes did not lead to a value
        return EvaluationResult.NOT_CHANGED

    def reset(self, dl: int) -> bool:
        """
        Reset based on decision level.

        Returns:
            bool: True if the variable was reset, False otherwise.

        Args:
            dl: Decision level threshold.
        """
        # self.set_expressions.reset(dl)
        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []
            return True
        return False

    def infer(self) -> set[int]:
        """
        Curently this returns an empty set as it does not support any inferences.
        This is here for compatibility with the VariableType protocol.
        """

        return set()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SetVariable):
            return False
        return self.var == value.var and self.set_expressions == value.set_expressions

    def __hash__(self) -> int:
        return hash((self.var, self.set_expressions))

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
        is_user_variable: Whether this variable is defined by the user or is an internal variable
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int, is_user_variable: bool = False) -> None:
        """
        Initialize a DictVariable.

        Args:
            name: Name of the dict variable.
            var: Clingo symbol identifying the variable.
            lit: Literal for the dict declaration.
            is_user_variable: Whether this variable is defined by the user or is an internal variable.
        """
        self.name: str = name
        self.var: clingo.Symbol = var
        self.dict_expressions: dict[VariableValue, SetVariableValue] = {}
        self.is_user_variable: bool = is_user_variable

        self.value: ValueStatus | multimap.Multimap[clingo.Symbol, Any] = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = DEFAULT_DECISION_LEVEL

        self.expressions_count: int = 0
        self.expressions_evaluated_counter: int = 0

        self.parents: list[VariableType] = []

        self.errors: propagator_warning_t = []

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return the set of VariableValue instances representing possible keys and their associated values.

        Returns:
            set[VariableValue]: Set of possible key expressions.
        """
        exprs = set()
        for key, value in self.dict_expressions.items():
            exprs.add(key)
            exprs.update(value.expressions)
        return exprs

    def add_value(self, key_value: VariableValue, value: VariableValue) -> None:
        """
        Add a key-value pair to the dict variable.

        Args:
            key_value: Interned expression for the key.
            value: Interned expression for the value.
        """
        # order is important, first we check if the expression exists to increase counter, then we add it to the dict
        # if we add it to the dict first, the check for the counter will not trigger for new expressions
        if key_value not in self.expressions:
            self.expressions_count += 1

        if key_value not in self.dict_expressions:
            self.dict_expressions[key_value] = SetVariableValue()

        if value not in self.expressions:
            self.expressions_count += 1
        self.dict_expressions[key_value].add_value(value)

    def has_domain(self) -> bool:
        """
        Check if the dict variable has a domain (any key-value pairs).

        Returns:
            bool: True if there are key-value pairs, False otherwise.
        """
        return len(self.dict_expressions) > 0

    def get_errors(self) -> propagator_warning_t:
        """
        Get all errors from the dict variable and its key-value pairs.
        Bad value warnings are filtered out for non user variables.

        Returns:
            propagator_warning_t: List of warnings or errors.
        """
        errors: propagator_warning_t = []
        for key, value in self.dict_expressions.items():
            errors.extend(key.get_errors() + value.get_errors())

            if self.is_user_variable:
                bad_value_warning = create_bad_value_warning(self)
                if bad_value_warning is not None:
                    errors.append(bad_value_warning)

        return errors + self.errors

    def get_literals(self, active: bool) -> set[int]:
        """
        Return the literals associated with the dict variable.

        Args:
            active: Whether to return active (signed) literals that give this variable its value or all literals.

        Returns:
            set[int]: Set of literals.
        """
        lits = set()
        for key, value in self.dict_expressions.items():
            if active:
                lits.update(value.active_literals)
                lits.update(key.active_literals)
            else:
                lits.update(value.literals)
                lits.update(key.literals)

        return lits

    @property
    def literals(self) -> set[int]:
        """
        Return the literal associated with this expression

        Returns:
            set[int]: A singleton set containing the literal
        """
        lits = self.get_literals(active=False)
        lits.add(self.literal)
        return lits

    @property
    def active_literals(self) -> set[int]:
        """
        Return literals relevant for this variable's current state.

        Includes literals from all key/value expressions and, if assigned,
        the dict declaration literal.

        Returns:
            set[int]: Set of literals.
        """
        lits = self.get_literals(active=True)

        if self.assigned is not None:
            if self.assigned:
                lits.add(self.literal)
            else:
                lits.add(-self.literal)

        return lits

    def get_value(self) -> ValueStatus | multimap.Multimap[clingo.Symbol, Any]:
        """
        Get the current value of the dict variable.

        Returns:
            ValueStatus | multimap.Multimap[clingo.Symbol, Any]: Current dict value or NOT_SET.
        """
        return self.value

    def discern_value(self) -> ValueStatus | multimap.Multimap[clingo.Symbol, Any]:
        """
        Returns a dictionary mapping keys to their assigned values.
        If any value is unassigned, returns None for that key.

        Returns:
            ValueStatus | multimap.Multimap[clingo.Symbol, Any]: The discerned value of the dict variable, or NOT_SET if any key/value is unassigned.
        """
        result: dict[clingo.Symbol, Any] = {}
        for key, value in self.dict_expressions.items():
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
        return multimap.Multimap(result)

    def has_unassigned(self) -> bool:
        """
        Check whether any key/value expression is still unassigned.

        Returns:
            bool: True if any key/value expression is unassigned.
        """
        return any(key.assigned is None or value.has_unassigned() for key, value in self.dict_expressions.items())

    def vars(self) -> set[clingo.Symbol]:
        """
        Collect all variables referenced by this dict.

        Returns:
            set[clingo.Symbol]: Variables used in key/value expressions.
        """
        vars = set()
        for key, value in self.dict_expressions.items():
            vars.update(value.vars())
            vars.update(key.vars())
        return vars

    def evaluate(
        self,
        ctl: clingo.PropagateControl,
    ) -> EvaluationResult:
        """
        Evaluate all values in the dictionary and return (changed, conflict).
        For DictVariable, conflict should never occur.

        Args:
            ctl: Clingo propagate control object.

        Returns:
            EvaluationResult: The result of the evaluation, indicating whether the value changed, remained the same, or if there was a conflict.
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
            return EvaluationResult.CHANGED

        if not self.has_unassigned():
            self.value = self.discern_value()
            if self.value != ValueStatus.NOT_SET:
                # only update decision level if we have a value
                self.decision_level = ctl.assignment.decision_level
                return EvaluationResult.CHANGED

        # if nothing changed or the changes did not lead to a value
        return EvaluationResult.NOT_CHANGED

    def reset(self, dl: int) -> bool:
        """
        Reset based on the decision level.

        Args:
            dl: Decision level threshold.
        Returns:
            bool: True if the variable was reset, False otherwise.
        """

        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = ValueStatus.NOT_SET
            self.errors = []
            return True
        return False

    def infer(self) -> set[int]:
        """
        Curently this return an empty set as it does not support any inferences.
        This is here for compatibility with the VariableType protocol.

        Returns:
            set[int]: A set of inferred values, currently always empty.
        """

        return set()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DictVariable):
            return False
        return self.var == other.var and self.dict_expressions == other.dict_expressions

    def __hash__(self) -> int:
        return hash((self.var, frozenset(self.dict_expressions.items())))

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
        self.opt_expressions: list[tuple[clingo.Symbol, VariableValue]] = []
        self.value: int | float = -sys.maxsize
        self.priority: int = priority
        self.decision_level: int = DEFAULT_DECISION_LEVEL

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return the set of VariableValue instances representing the expressions in the optimization sum.

        Returns:
            set[VariableValue]: Set of expressions in the optimization sum.
        """
        return {expr for _, expr in self.opt_expressions}

    def add_value(
        self,
        var: clingo.Symbol,
        value: VariableValue,
    ) -> None:
        """
        Add a value to the optimization sum.

        Args:
            var: Clingo symbol for the variable.
            value: Interned expression to evaluate.
        """
        self.opt_expressions.append((var, value))

    def get_literals(self, active: bool) -> set[int]:
        """
        Get all literals associated with the optimization sum.

        Args:
            active: Whether to return active (signed) literals that give this variable its value or all literals.

        Returns:
            set[int]: Set of literals.
        """
        lits = set()
        for var, expr in self.opt_expressions:
            if active:
                lits.update(expr.active_literals)
            else:
                lits.update(expr.literals)
        return lits

    @property
    def literals(self) -> set[int]:
        """
        Get all literals associated with the optimization sum.

        Returns:
            set[int]: Set of literals.
        """
        return self.get_literals(active=False)

    @property
    def active_literals(self) -> set[int]:
        """
        Get all literals associated with the optimization sum that gave it its current value.

        Returns:
            set[int]: Set of literals.
        """
        return self.get_literals(active=True)

    def discern_value(self) -> int | float:
        """
        Compute the sum of all assigned values in the optimization sum.

        Returns:
            int | float: The sum of all assigned values.
        """
        vals = set()
        # TODO: check if we need to also need to excluce Bad.bad from the sums
        for var, expr in self.opt_expressions:
            if expr.value not in [ValueStatus.NOT_SET, ValueStatus.ASSIGNMENT_IS_FALSE, None, expression.Bad.bad]:
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
        for _, expr in self.opt_expressions:
            errors.extend(expr.get_errors())
        return errors

    def evaluate(
        self,
        ctl: clingo.PropagateControl,
    ) -> bool:
        """
        Evaluate the optimization sum and return True if the value has changed.

        Args:
            ctl: Clingo propagate control.

        Returns:
            bool: True if the value has changed, False otherwise.
        """
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
        for var, expr in self.opt_expressions:
            vars.update(expr.vars())
        return vars

    def reset(self, dl: int) -> None:
        """
        Reset the optimization sum if the decision level is greater than or equal to dl.

        Args:
            dl: Decision level threshold.
        """
        if self.decision_level >= dl:
            self.decision_level = DEFAULT_DECISION_LEVEL
            self.value = -sys.maxsize

    def has_unassigned(self) -> bool:
        """
        Check if any value in the optimization sum is unassigned.

        Returns:
            bool: True if any value is unassigned, False otherwise.
        """
        return any(expr.value == ValueStatus.NOT_SET for var, expr in self.opt_expressions)

    def __repr__(self) -> str:
        return f"OptimizationSum({self.opt_expressions})"


class OptimizationHandler:
    """
    Handles multiple optimization sums, each with a priority.

    Attributes:
        sums: List of OptimizationSum instances.
              Note that this is a list and not a dict.
              OptimizationSums are ordered by priority, with higher priority sums coming first.
    """

    def __init__(self) -> None:
        """
        Initialize an OptimizationHandler.
        """
        self.sums: list[OptimizationSum] = []

    @property
    def expressions(self) -> set[VariableValue]:
        """
        Return the set of VariableValue instances representing all expressions in all optimization sums.

        Returns:
            set[VariableValue]: Set of expressions in all optimization sums.
        """
        exprs = set()
        for _sum in self.sums:
            exprs.update(_sum.expressions)
        return exprs

    def add_value(self, var: clingo.Symbol, value: VariableValue, priority: int = 0) -> None:
        """
        Add a value to the appropriate optimization sum by priority.

        Args:
            var: Clingo symbol for the variable.
            value: Interned expression to evaluate.
            priority: Priority of the optimization sum.
        """
        for _sum in self.sums:
            if _sum.priority == priority:
                _sum.add_value(var, value)
                return
        new_sum = OptimizationSum(priority)
        new_sum.add_value(var, value)
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
        self,
        ctl: clingo.PropagateControl,
    ) -> bool:
        """
        Evaluate all optimization sums and return True if any value has changed.

        Args:
            ctl: Clingo propagate control.

        Returns:
            bool: True if any value has changed, False otherwise.
        """
        changed = False
        for _sum in self.sums:
            changed |= _sum.evaluate(ctl)
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

    def reset(self, dl: int) -> None:
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

    @property
    def literals(self) -> set[int]:
        """
        Returns the empty set since the optimization sums do not have literals directly associated with them.

        Returns:
            set[int]: Empty set.
        """
        return set()

    @property
    def active_literals(self) -> set[int]:
        """
        Returns the empty set since the optimization sums do not have literals directly associated with them.

        Returns:
            set[int]: Empty set.
        """
        return set()


class Evaluations:
    """
    Manages the current evaluations of variables.

    Attributes:
        evaluations: Dictionary mapping variable symbols to their evaluated values.
        false_assignments: List of variables that are assigned false.
        existing_vars: List of variables that exist in the current evaluation.
    """

    def __init__(self) -> None:
        """
        Initialize Evaluations with an empty dictionary.
        """
        self.evaluations: evaluations_type = {}
        self.false_assignments: list[clingo.Symbol] = []
        # for each variable, it also counts how many different types it can have.
        # this is needed for the check to see if the variable is usable in the current evaluation.
        self.existing_vars: dict[clingo.Symbol, int] = {}

    def init(self, variables: Iterable[VariableType]) -> None:
        """
        Initialize the existing variables list based on the provided variables.
        This method should be called before any evaluations are updated
        to ensure that the existing variables are correctly tracked.

        Args:
            variables: Iterable of variables to initialize from.
        """
        for var in variables:
            self.existing_vars[var.var] = self.existing_vars.get(var.var, 0) + 1

    def add_var_to_evaluations(self, variable: VariableType) -> None:
        """
        Add a value-bearing variable's value to this evaluation context.

        Args:
            variable: The variable to add.
        """
        if isinstance(variable, BoolEvaluateVariable):
            return

        value = variable.get_value()
        if value == ValueStatus.NOT_SET:
            return
        if value == ValueStatus.ASSIGNMENT_IS_FALSE:
            self.false_assignments.append(variable.var)
            return

        self.evaluations[variable.var] = value

    def remove_var_from_evaluations(self, variable: VariableType) -> None:
        """
        Remove a value-bearing variable's contribution from this context.

        Args:
            variable: The variable to remove.
        """
        if isinstance(variable, BoolEvaluateVariable):
            return

        res = self.evaluations.pop(variable.var, None)

        if res is not None:
            return

        try:
            self.false_assignments.remove(variable.var)
            return
        except ValueError:
            pass

    def var_usable(self, var: clingo.Symbol) -> bool:
        """
        Check if a variable is usable in the current evaluation.

        A variable is considered usable if it has an assigned value, is listed as a false assignment or does not exist.

        Args:
            var: Variable symbol to check.

        Returns:
            bool: True if the variable is usable, False otherwise.

        """
        # return var in self.evaluations or var in self.false_assignments or var not in self.existing_vars
        if var not in self.existing_vars:
            return True

        appearances = 0
        if var in self.evaluations:
            appearances += 1
        if var in self.false_assignments:
            appearances += 1
        return appearances == self.existing_vars[var]


type VariableTypeNames = Literal[
    Variable.__name__,  # ty: ignore[invalid-type-form]
    SetVariable.__name__,  # ty: ignore[invalid-type-form]
    DictVariable.__name__,  # ty: ignore[invalid-type-form]
    BoolEvaluateVariable.__name__,  # ty: ignore[invalid-type-form]
]
