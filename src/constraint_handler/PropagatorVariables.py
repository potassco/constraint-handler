from __future__ import annotations

import sys
from abc import abstractmethod
from typing import Any, Iterable, Protocol

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.solver_environment as solver_environment
from constraint_handler.PropagatorConstants import (
    DEBUG_PRINT,
    EXECUTION_INPUT,
    EXECUTION_OUTPUT,
    FALSE_ASSIGNMENTS,
    EvaluationResult,
    ValueStatus,
)


def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)


class VariableType(Protocol):
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
    def get_errors(self) -> list[Exception]: ...

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
    This class corresponds to a single expression appearing in some assingment atom
    """

    def __init__(self, expr: expression.Expr, lit: int):
        self.expr: expression.Expr = expr
        self.value: Any = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = sys.maxsize

        self.errors: list[Exception] = []

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """
        Evaluate the expression and return True if the value has changed.
        We assume that a value can only be evaluated if all its variables are assigned.
        If a value already exists(I.e, not ValueStatus.NOT_SET) then we do not evaluate again.
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
            if var not in evaluations:  # and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.value == ValueStatus.NOT_SET
                return False

        self.value, self.errors = evaluator.evaluate_expr(self.expr, env, evaluations)
        myprint(f"{self.expr} evaluated to {self.value}")

        self.decision_level = min(self.decision_level, ctl.assignment.decision_level)
        return True

    def get_errors(self) -> list[Exception]:
        return self.errors

    def vars(self) -> frozenset[clingo.Symbol]:
        return evaluator.collectVars(self.expr)

    def reset(self, dl):
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET
            self.decision_level = sys.maxsize
            self.assigned = None
            self.errors = []

    @property
    def literals(self) -> set[int]:
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
    def __init__(self, op: expression.Operator, args: list[expression.Expr], literal: int = -1):
        self.op: expression.Operator = op
        self.args: list[expression.Expr] = args
        self.value: Any = ValueStatus.NOT_SET
        self.literal: int = literal

        self.errors: list[Exception] = []

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        if not ctl.assignment.is_true(self.literal):
            return False
        myprint(f"Evaluating {self.op}({self.args})")
        value, self.errors = evaluator.evaluate_expr(expression.Operation(self.op, self.args), env, evaluations)
        self.value = value
        return True

    def get_value(self) -> Any:
        return self.value

    def get_errors(self) -> list[Exception]:
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
    __var = clingo.Function("ensure")

    def __init__(self, name: str, expr: expression.Expr, literal: int):
        self.name: str = name
        self.expression: VariableValue = VariableValue(expr, literal)

        self.value: ValueStatus | bool = ValueStatus.NOT_SET

    @property
    def var(self) -> clingo.Symbol:
        return self.__var

    @property
    def parents(self) -> list[VariableType]:
        return []

    def has_domain(self) -> bool:
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
        # assert isinstance(self.value, bool), "EnsureVariable evaluated to non-boolean value"

        conflict = self.value is False or self.value is None
        if conflict:
            return EvaluationResult.CONFLICT

        return EvaluationResult.CHANGED

    def get_value(self) -> ValueStatus | bool:
        return self.value

    def has_unassigned(self) -> bool:
        return self.value == ValueStatus.NOT_SET

    def vars(self) -> set[clingo.Symbol]:
        return set(self.expression.vars())

    def get_errors(self) -> list[Exception]:
        return self.expression.get_errors()

    @property
    def literals(self) -> set[int]:
        return self.expression.literals

    @property
    def decision_level(self) -> int:
        return self.expression.decision_level

    def reset(self, dl: int) -> None:
        self.expression.reset(dl)
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        return

    def __hash__(self):
        return hash((self.name, self.expression))

    def __repr__(self) -> str:
        return f"EnsureVariable(name={self.name}, expression={self.expression})"


class Variable:
    """
    A variable with a name and a value expression.
    This is supposed to mirror the assign/3 atom(also propagator_assign/3) in the ASP encoding.
    """

    def __init__(self, name: str, var: clingo.Symbol):
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: set[VariableValue] = set()
        self.value: Any = ValueStatus.NOT_SET
        self.parents: list[VariableType] = []
        self.decision_level: int = sys.maxsize

    def add_value(self, expr: expression.Expr, lit: int) -> None:
        self.expressions.add(VariableValue(expr, lit))

    def get_value(self) -> Any:
        return self.value

    def get_errors(self) -> list[Exception]:
        errors: list[Exception] = []
        for var_value in self.expressions:
            errors.extend(var_value.get_errors())
        return errors

    def has_unassigned(self) -> bool:
        return any(var_value.value == ValueStatus.NOT_SET for var_value in self.expressions)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for value in self.expressions:
            vars.update(value.vars())
        return vars

    def has_domain(self) -> bool:
        return len(self.expressions) > 0

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict (multiple values assigned).
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
            return EvaluationResult.CONFLICT
        elif len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                val = [ValueStatus.NOT_SET]
            else:
                # if all values are set and none are true, then it is set to false assignment
                self.decision_level = ctl.assignment.decision_level
                self.value = ValueStatus.ASSIGNMENT_IS_FALSE
                return EvaluationResult.CONFLICT

        elif len(val) == 1:
            if val[0] == self.value:
                # same value as before
                return EvaluationResult.NOT_CHANGED

        self.decision_level = ctl.assignment.decision_level
        self.value = val[0]
        return EvaluationResult.CHANGED

    def get_values(self) -> list[Any]:
        vals = [
            value.value
            for value in self.expressions
            if value.value != ValueStatus.NOT_SET and value.value != ValueStatus.ASSIGNMENT_IS_FALSE
        ]
        return vals

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.expressions:
            lits.update(value.literals)
        return lits

    def reset(self, dl: int) -> None:
        for value in self.expressions:
            value.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = sys.maxsize
            self.value = ValueStatus.NOT_SET

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore

        d[self.var] = value  # type: ignore

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
    def __init__(self) -> None:
        self.values: set[VariableValue] = set()

    def has_domain(self) -> bool:
        return len(self.values) > 0

    def add_value(self, arg: expression.Expr, lit: int) -> None:
        self.values.add(VariableValue(arg, lit))

    def get_errors(self) -> list[Exception]:
        errors: list[Exception] = []
        for var_value in self.values:
            errors.extend(var_value.get_errors())
        return errors

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.values:
            lits.update(value.literals)
        return lits

    @property
    def decision_level(self) -> int:
        return min(value.decision_level for value in self.values)

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
        return any(arg.value == ValueStatus.NOT_SET for arg in self.values)

    def vars(self) -> set[clingo.Symbol]:
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
    set_declare is this class, while each set_assign adds a value to the set(which uses the SetVariableValue class).
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: SetVariableValue = SetVariableValue()

        self.value: ValueStatus | frozenset[Any] = ValueStatus.NOT_SET

        self.literal: int = lit  # this is the literal for the set declaration
        self.assigned: bool | None = None  # Truth value of the set declaration
        self.decision_level: int = sys.maxsize  # decision level of the set declaration

        self.parents: list[VariableType] = []

        self.errors: list[Exception] = []

    def has_domain(self) -> bool:
        return self.expressions.has_domain()

    def add_value(self, arg: expression.Expr, lit: int) -> None:
        self.expressions.add_value(arg, lit)

    def get_errors(self) -> list[Exception]:
        return self.expressions.get_errors() + self.errors

    @property
    def literals(self) -> set[int]:
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
        return self.expressions.has_unassigned()

    def vars(self) -> set[clingo.Symbol]:
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
            self.errors.append(ValueError(f"Set declaration for {self.var} is False!"))
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
        self.expressions.reset(dl)
        if self.decision_level >= dl:
            self.decision_level = sys.maxsize
            self.value = ValueStatus.NOT_SET
            self.errors = []

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore

        d[self.var] = value  # type: ignore

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
    multimap_declare is this class, while each multimap_assign adds a key-value pair to the dict(which uses the SetVariableValue class).
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: dict[VariableValue, SetVariableValue] = multimap.HashableDict()

        self.value: ValueStatus | dict[clingo.Symbol, Any] = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = sys.maxsize

        self.parents: list[VariableType] = []

        self.errors: list[Exception] = []

    def add_value(self, key: expression.Expr, expr: expression.Expr, lit: int) -> None:
        # setting lit for key to 1 since it does not have its own literal
        # the literal is bound for the value!
        key_val = VariableValue(key, 1)
        if key_val not in self.expressions:
            self.expressions[key_val] = SetVariableValue()
        self.expressions[key_val].add_value(expr, lit)

    def has_domain(self) -> bool:
        return len(self.expressions) > 0

    def get_errors(self) -> list[Exception]:
        errors: list[Exception] = []
        for key, value in self.expressions.items():
            errors.extend(key.get_errors())
            errors.extend(value.get_errors())
        return errors + self.errors

    @property
    def literals(self) -> set[int]:
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
        return any(value.has_unassigned() for value in self.expressions.values())

    def vars(self) -> set[clingo.Symbol]:
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
            self.errors.append(ValueError(f"Dict declaration for {self.var} is False!"))
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
        for value in self.expressions.values():
            value.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = sys.maxsize
            self.value = ValueStatus.NOT_SET
            self.errors = []

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
        value = self.get_value()
        if value == ValueStatus.NOT_SET:
            return
        elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
            d[FALSE_ASSIGNMENTS].append(self.var)  # type: ignore

        d[self.var] = value  # type: ignore

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
    def __init__(self, priority: int = 0) -> None:
        self.expressions: list[tuple[clingo.Symbol, VariableValue]] = []
        self.value: int | float = -sys.maxsize
        self.priority: int = priority
        self.decision_level: int = sys.maxsize

    def add_value(self, var: clingo.Symbol, expr: expression.Expr, lit: int) -> None:
        self.expressions.append((var, VariableValue(expr, lit)))

    @property
    def literals(self) -> set[int]:
        lits = set()
        for var, expr in self.expressions:
            lits.update(expr.literals)
        return lits

    def discern_value(self) -> int | float:
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
        return self.value

    def get_errors(self) -> list[Exception]:
        errors: list[Exception] = []
        for _, expr in self.expressions:
            errors.extend(expr.get_errors())
        return errors

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        """Evaluate the expression and return True if the value has changed."""
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
        vars = set()
        for var, expr in self.expressions:
            vars.update(expr.vars())
        return vars

    def reset(self, dl: int):
        for var, expr in self.expressions:
            expr.reset(dl)

        if self.decision_level >= dl:
            self.decision_level = sys.maxsize
            self.value = -sys.maxsize

    def has_unassigned(self) -> bool:
        return any(expr.value == ValueStatus.NOT_SET for var, expr in self.expressions)

    def __repr__(self) -> str:
        return f"OptimizationSum({self.expressions})"


class OptimizationHandler:
    def __init__(self):
        self.sums: list[OptimizationSum] = []

    def add_value(self, var: clingo.Symbol, expr: expression.Expr, lit: int, priority: int = 0) -> None:
        for _sum in self.sums:
            if _sum.priority == priority:
                _sum.add_value(var, expr, lit)
                return
        new_sum = OptimizationSum(priority)
        new_sum.add_value(var, expr, lit)
        self.sums.append(new_sum)

        self.sums.sort(key=lambda x: x.priority, reverse=True)  # higher priority first

    def get_sum_count(self) -> int:
        return len(self.sums)

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.PropagateControl, env: dict[Any, Any]
    ) -> bool:
        changed = False
        for _sum in self.sums:
            changed |= _sum.evaluate(evaluations, ctl, env)
        return changed

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for _sum in self.sums:
            vars.update(_sum.vars())
        return vars

    def reset(self, dl: int):
        for _sum in self.sums:
            _sum.reset(dl)

    def get_errors(self) -> list[Exception]:
        errors: list[Exception] = []
        for _sum in self.sums:
            errors.extend(_sum.get_errors())
        return errors

    def get_value(self) -> list[int | float]:
        return [_sum.get_value() for _sum in self.sums]

    def has_unassigned(self, position: int) -> bool:
        """
        Note that position is the index of the optimization sum in the sums list, which is sorted by priority.
        So position 0 is the highest priority sum, position 1 is the second highest priority sum, and so on.
        It is NOT the priority!
        """
        return self.sums[position].has_unassigned()


class Execution:
    def __init__(
        self,
        name: str,
        func_name: clingo.Symbol,
        stmt: statement.Stmt,
        in_vars: list[clingo.Symbol],
        out_vars: list[clingo.Symbol],
    ):
        self.name: str = name
        self.func_name: clingo.Symbol = func_name
        self.stmt: statement.Stmt = stmt
        self.in_vars: list[clingo.Symbol] = in_vars
        self.converted_in_vars: list[clingo.Symbol] = self.convert_vars(in_vars, input=True)
        self.out_vars: list[clingo.Symbol] = out_vars
        self.converted_out_vars: list[clingo.Symbol] = self.convert_vars(out_vars, input=False)

        # this is for the execution run atom
        # assuming the declaration atom is always a fact?
        # otherwise, we might need a literal for that as well
        # if there is no execution_run atom, this is always false, which means the execution is never run
        self.literal: int = -1
        self.assigned: bool | None = None

        self.decision_level: int = sys.maxsize

        self.values: ValueStatus | list[tuple[clingo.Symbol, Any]] = ValueStatus.NOT_SET

        self.parents: list[VariableType] = []

        self.errors: list[Exception] = []

    def has_domain(self) -> bool:
        return True  # executions always have a domain

    def has_unassigned(self) -> bool:
        return self.values == ValueStatus.NOT_SET

    @property
    def var(self) -> clingo.Symbol:
        return self.func_name

    @property
    def literals(self) -> set[int]:
        """
        Return the literal(s) associated with this execution.
        If the execution is run return the positive literal.
        If the execution is not run return the negative literal.
        If the execution is unassigned return an empty set.
        """
        if self.assigned:
            return {self.literal}
        elif self.assigned is False:
            return {-self.literal}
        else:
            return set()

    def convert_vars(self, vars: list[clingo.Symbol], input=True) -> list[clingo.Symbol]:
        """
        Convert the name of the variable from e.g. x to execution_input(fname, x)
        """
        converted: list[clingo.Symbol] = []
        for var in vars:
            converted.append(self.convert_var(var, input=input))
        return converted

    def convert_var(self, var: clingo.Symbol | str, input=True) -> clingo.Symbol:
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
        """Evaluate the execution and return True if the value has changed."""
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
            if var not in evaluations:  # and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.values == ValueStatus.NOT_SET
                return EvaluationResult.NOT_CHANGED

        evals = {}
        for c_var, var in zip(self.converted_in_vars, self.in_vars):
            evals[var] = evaluations[c_var]

        try:
            self.errors = evaluator.evaluate_stmt(self.stmt, env, evals)
        except solver_environment.FailIntegrityExn:
            self.decision_level = ctl.assignment.decision_level
            return EvaluationResult.CONFLICT

        self.values: list[tuple[clingo.Symbol, Any]] = []
        for c_out_var, out_var in zip(self.converted_out_vars, self.out_vars):
            if out_var not in evals:
                self.values.append((c_out_var, None))
            else:
                self.values.append((c_out_var, evals[out_var]))

        return EvaluationResult.CHANGED

    def get_value(self) -> ValueStatus | list[tuple[clingo.Symbol, Any]]:
        return self.values

    def get_errors(self) -> list[Exception]:
        return self.errors

    def add_run_literal(self, lit: int):
        self.literal = lit

    def vars(self) -> set[clingo.Symbol]:
        return set(self.converted_in_vars)

    def reset(self, dl: int):
        if self.decision_level >= dl:
            self.decision_level = sys.maxsize
            self.errors = []
            self.values = ValueStatus.NOT_SET

    def add_self_to_dict(self, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
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
        return hash((self.func_name, self.stmt, tuple(self.in_vars), tuple(self.out_vars)))

    def __repr__(self) -> str:
        return f"Execution({self.name}, {self.func_name}, {self.stmt})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Execution):
            return False
        return (
            self.func_name == other.func_name
            and self.stmt == other.stmt
            and self.in_vars == other.in_vars
            and self.out_vars == other.out_vars
        )


def make_dict_from_variables(
    variables: Iterable[VariableType],
) -> dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]:
    result: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]] = {}
    for var in variables:
        var.add_self_to_dict(result)

    return result
