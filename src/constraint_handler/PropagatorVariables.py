from __future__ import annotations

import sys
from typing import Any, Sequence, TypeVar

import clingo

import constraint_handler.evaluator as evaluator
from constraint_handler.PropagatorConstants import DEBUG_PRINT, FALSE_ASSIGNMENTS, ValueStatus, EvaluationResult


def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)


VariableType = TypeVar("VariableType", "Variable", "SetVariable", "DictVariable", "Execution")


class EvaluateVariable:

    def __init__(self, op: evaluator.Operator, args: list[evaluator.Expr], literal: int = -1):
        self.op: evaluator.Operator = op
        self.args: list[evaluator.Expr] = args
        self.value: Any = ValueStatus.NOT_SET
        self.literal: int = literal

    def evaluate(self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        if not ctl.assignment.is_true(self.literal):
            return False
        myprint(f"Evaluating {self.op}({self.args})")
        value, errors = evaluator.evaluate_expr(
            evaluator.Operation(self.op, self.args), env, evaluations
        )  # TODO: do something with errors?
        self.value = value
        return True

    def get_value(self) -> Any:
        return self.value

    def __eq__(self, other):
        if not isinstance(other, EvaluateVariable):
            return False
        return self.op == other.op and self.args == other.args and self.literal == other.literal

    def __hash__(self):
        return hash((str(self.op), str(self.args), self.literal))


class VariableValue:
    """
    This class corresponds to a single expression appearing in some assingment atom
    """

    def __init__(self, expr: evaluator.Expr, lit: int):
        self.expr: evaluator.Expr = expr
        self.value: Any = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = sys.maxsize

    def evaluate(self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]) -> bool:
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
            if var not in evaluations and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.value == ValueStatus.NOT_SET
                return False

        self.value, errors = evaluator.evaluate_expr(self.expr, env, evaluations)  # TODO: do something with errors?
        myprint(f"{self.expr} evaluated to {self.value}")

        self.decision_level = ctl.assignment.decision_level
        return True

    def vars(self) -> set[clingo.Symbol]:
        return evaluator.collectVars(self.expr)

    def reset(self, dl):
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET
            self.decision_level = sys.maxsize
            # TODO: it is possible that it is still assigned!
            # Maybe add a second property self.assigned_decision_level?
            # that one would be only to know when the variable was assigned
            # but not when it got a value!
            # then we could reset this only if self.assigned_decision_level >= dl?
            # Maybe important for the self.literals call of Variables and so on
            # since they check for this property
            # Maybe we should just extend those to check for the value only,
            # and not the assignment of the literal?
            self.assigned = None

    def __eq__(self, other):
        if not isinstance(other, VariableValue):
            return False
        return self.expr == other.expr

    def __hash__(self):
        return hash(str(self.expr))

    def __str__(self):
        return f"VariableValue({self.expr}, {self.value})"

    def __repr__(self):
        return f"VariableValue({self.expr}, {self.value})"


class EnsureVariable:

    __var = clingo.Function("ensure")

    def __init__(self, name: str, expr: evaluator.Expr, literal: int):
        self.name: str = name
        self.expression: VariableValue = VariableValue(expr, literal)
        
        self.value: ValueStatus | bool = ValueStatus.NOT_SET

    @property
    def var(self) -> clingo.Symbol:
        return self.__var
    
    @property
    def parents(self) -> list[VariableType]:
        return []

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict.
        """
        if ctl.assignment.is_false(self.expression.literal):
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
        return self.expression.vars()

    @property
    def literals(self) -> set[int]:
        return {self.expression.literal}

    @property
    def decision_level(self) -> int:
        return self.expression.decision_level
    
    def reset(self, dl: int) -> None:
        self.expression.reset(dl)
        if self.decision_level >= dl:
            self.value = ValueStatus.NOT_SET

    def __hash__(self):
        return hash((self.name, self.expression))


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

    def add_value(self, expr: evaluator.Expr, lit: int) -> None:
        self.expressions.add(VariableValue(expr, lit))

    def get_value(self) -> Any:
        return self.value

    def has_unassigned(self) -> bool:
        return any(var_value.value == ValueStatus.NOT_SET for var_value in self.expressions)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for value in self.expressions:
            vars.update(value.vars())
        return vars

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]
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
            myprint(f"Variable vals: {val}")
            return EvaluationResult.CONFLICT
        elif len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                val = {ValueStatus.NOT_SET}
            else:
                # if all values are set and none are true, then it is set to false assignment
                val = {ValueStatus.ASSIGNMENT_IS_FALSE}
        elif len(val) == 1:
            if val == self.value:
                # same value as before
                return EvaluationResult.NOT_CHANGED

        self.decision_level = ctl.assignment.decision_level
        self.value = val.pop()
        return EvaluationResult.CHANGED

    def get_values(self) -> set[Any]:
        vals = set(
            value.value
            for value in self.expressions
            if value.value != ValueStatus.NOT_SET and value.value != ValueStatus.ASSIGNMENT_IS_FALSE
        )
        return vals

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.expressions:
            if value.value != ValueStatus.NOT_SET:
                if value.assigned:
                    lits.add(value.literal)
                else:
                    lits.add(-value.literal)
        return lits

    def reset(self, dl: int) -> None:
        for value in self.expressions:
            value.reset(dl)

        # only get a new value if the decision level was higher than
        # what the variable has.
        # If dl is still higher, this means that some values might have been reset
        # but they had no impact on this variable's value
        if self.decision_level < dl:
            return

        val = self.get_values()
        if len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                self.value = ValueStatus.NOT_SET
            else:
                # if all values are set and none are true, then it is set to false assignment
                self.value = ValueStatus.ASSIGNMENT_IS_FALSE
        elif len(val) == 1:
            self.value = val.pop()
        else:
            print(f"Reset variable {self.name} at decision level {dl}, values after reset: {val}")
            assert False, "Variable has multiple values after reset, should not happen"

    def __eq__(self, other):
        if not isinstance(other, Variable):
            assert False, "Variable can only be compared to another Variable"
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self):
        return hash((self.var, frozenset(self.expressions)))

    def __str__(self):
        return f"Variable({self.name}, {self.var}, {self.literals}, {self.expressions})"


class SetVariableValue:
    def __init__(self):
        self.values: set[VariableValue] = set()

    def add_value(self, arg: evaluator.Expr, lit: int) -> None:
        self.values.add(VariableValue(arg, lit))

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.values:
            if value.value != ValueStatus.NOT_SET:
                if value.assigned:
                    lits.add(value.literal)
                else:
                    lits.add(-value.literal)
        return lits

    @property
    def decision_level(self) -> int:
        return min(value.decision_level for value in self.values)

    def get_value(self) -> ValueStatus | set[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        if self.has_unassigned():
            return ValueStatus.NOT_SET
        # Note that we let None be a part of the set!
        return {arg.value for arg in self.values if arg.value != ValueStatus.ASSIGNMENT_IS_FALSE}

    def has_unassigned(self) -> bool:
        return any(arg.value == ValueStatus.NOT_SET for arg in self.values)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for arg in self.values:
            vars.update(arg.vars())
        return vars

    def evaluate(self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        changed = False
        for arg in self.values:
            changed |= arg.evaluate(evaluations, ctl, env)

        return changed

    def reset(self, dl: int):
        for arg in self.values:
            arg.reset(dl)

    def __eq__(self, other):
        if not isinstance(other, SetVariableValue):
            return False
        return self.values == other.values

    def __hash__(self):
        return hash(frozenset(self.values))

    def __str__(self):
        return f"SetVariableValue({self.values})"


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

        self.value: ValueStatus | set[Any] = ValueStatus.NOT_SET

        self.literal: int = lit  # this is the literal for the set declaration
        self.assigned: bool | None = None  # Truth value of the set declaration
        self.decision_level: int = sys.maxsize  # decision level of the set declaration

        self.parents: list[VariableType] = []

    def add_value(self, arg: evaluator.Expr, lit: int) -> None:
        self.expressions.add_value(arg, lit)

    @property
    def literals(self) -> set[int]:
        lits = self.expressions.literals
        lits.add(self.literal)
        return lits

    def get_value(self) -> ValueStatus | set[Any]:
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
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]
    ) -> EvaluationResult:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict.
        For sets, there should never be a conflict.
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

        changed = self.expressions.evaluate(evaluations, ctl, env)

        if changed:
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

    def __eq__(self, value):
        if not isinstance(value, SetVariable):
            assert False, "SetVariable can only be compared to another SetVariable"
        return self.var == value.var and self.expressions == value.expressions

    def __hash__(self):
        return hash((self.var, self.expressions))

    def __str__(self):
        return f"SetVariable({self.name}, {self.var})"


class DictVariable:
    """
    A dict variable with a name and a set of key-value expressions.
    This is supposed to mirror the multimap_declare/2 and multimap_assign/4 atom in the ASP encoding.
    multimap_declare is this class, while each multimap_assign adds a key-value pair to the dict(which uses the SetVariableValue class).
    """

    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name: str = name
        self.var: clingo.Symbol = var
        self.expressions: dict[VariableValue, SetVariableValue] = evaluator.HashableDict()

        self.value: ValueStatus | dict[clingo.Symbol, Any] = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = sys.maxsize

        self.parents: list[VariableType] = []

    def add_value(self, key: evaluator.Expr, expr: evaluator.Expr, lit: int) -> None:
        # setting lit for key to 1 since it does not have its own literal
        # the literal is bound for the value!
        key_val = VariableValue(key, 1)
        if key_val not in self.expressions:
            self.expressions[key_val] = SetVariableValue()
        self.expressions[key_val].add_value(expr, lit)

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.expressions.values():
            lits.update(value.literals)
        lits.add(self.literal)

        return lits

    def get_value(self) -> ValueStatus | dict[clingo.Symbol, Any]:
        return self.value

    def discern_value(self) -> ValueStatus | dict[clingo.Symbol, Any]:
        """
        Returns a dictionary mapping keys to their assigned values.
        If any value is unassigned, returns None for that key.
        """
        result = evaluator.HashableDict()
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
            if len(val) == 1:
                val = val.pop()
            result[key_val] = val
        return result

    def has_unassigned(self) -> bool:
        return any(value.has_unassigned() for value in self.expressions.values())

    def vars(self) -> set[clingo.Symbol]:
        # TODO: check if keys can also have variables
        vars = set()
        for value in self.expressions.values():
            vars.update(value.vars())
        return vars

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]
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
            return EvaluationResult.CHANGED

        changed = False
        for key, value in self.expressions.items():
            changed |= key.evaluate(evaluations, ctl, env)
            changed |= value.evaluate(evaluations, ctl, env)

        if changed:
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

    def __eq__(self, other):
        if not isinstance(other, DictVariable):
            assert False, "DictVariable can only be compared to another DictVariable"
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self):
        return hash((self.var, frozenset(self.expressions.items())))

    def __str__(self):
        return f"DictVariable({self.name}, {self.var})"


class OptimizationSum:
    def __init__(self):

        self.expressions: list[tuple[clingo.Symbol, VariableValue]] = []
        self.value: Any = ValueStatus.NOT_SET

        self.decision_level: int = sys.maxsize

    def add_value(self, var: clingo.Symbol, expr: evaluator.Expr, lit: int) -> None:
        self.expressions.append((var, VariableValue(expr, lit)))

    @property
    def literals(self) -> set[int]:
        lits = set()
        for var, expr in self.expressions:
            if expr.value != ValueStatus.NOT_SET:
                if expr.assigned:
                    lits.add(expr.literal)
                else:
                    lits.add(-expr.literal)
        return lits

    def get_value(self) -> Any:
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

    def evaluate(self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        changed = False
        # print(evaluations)
        for var, expr in self.expressions:
            changed |= expr.evaluate(evaluations, ctl, env)

        if changed:
            total = self.get_value()
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
            self.value = ValueStatus.NOT_SET

    def has_unassigned(self) -> bool:
        return any(expr.value == ValueStatus.NOT_SET for var, expr in self.expressions)


class Execution:

    def __init__(
        self,
        name: str,
        func_name: str,
        stmt: evaluator.Stmt,
        in_vars: list[clingo.Symbol],
        out_vars: list[clingo.Symbol],
    ):
        self.name: str = name
        self.func_name: str = func_name
        self.stmt: evaluator.Stmt = stmt
        self.in_vars: list[clingo.Symbol] = in_vars
        self.converted_in_vars: list[clingo.Symbol] = self.convert_vars(in_vars, input=True)
        self.out_vars: list[clingo.Symbol] = out_vars
        self.converted_out_vars: list[clingo.Symbol] = self.convert_vars(out_vars, input=False)

        # this is for the execution run atom
        # assuming the declaration atom is always a fact?
        # otherwise, we might need a literal for that as well
        self.literal: int = 0
        self.assigned: bool | None = None

        self.decision_level: int = sys.maxsize

        self.values: ValueStatus | list[tuple[clingo.Symbol, Any]] = ValueStatus.NOT_SET

        self.parents: list[VariableType] = []

    @property
    def var(self):
        return self.func_name

    @property
    def literals(self) -> set[int]:
        return {self.literal}

    def convert_vars(self, vars: list[clingo.Symbol], input=True) -> list[clingo.Symbol]:
        """
        Convert the name of the variable from e.g. x to execution_input(fname, x)
        """
        converted: list[clingo.Symbol] = []
        for var in vars:
            converted.append(self.convert_var(var, input=input))
        return converted

    def convert_var(self, var: clingo.Symbol, input=True) -> clingo.Symbol:
        exec_name: str = "execution_input" if input else "execution_output"
        var_func = var if type(var) == clingo.Symbol else clingo.String(var)
        v = clingo.Function(exec_name, [self.func_name, var_func])
        return v

    def evaluate(
        self, evaluations: dict[clingo.Symbol, Any], ctl: clingo.Control, env: dict[Any, Any]
    ) -> EvaluationResult:
        """Evaluate the execution and return True if the value has changed."""
        self.assigned = ctl.assignment.value(self.literal)
        if self.assigned is None:
            return EvaluationResult.NOT_CHANGED

        if self.values != ValueStatus.NOT_SET:
            # already assigned
            return EvaluationResult.NOT_CHANGED

        if ctl.assignment.is_false(self.literal):
            self.values = ValueStatus.ASSIGNMENT_IS_FALSE
            self.decision_level = ctl.assignment.decision_level
            return EvaluationResult.CHANGED

        for var in self.converted_in_vars:
            if var not in evaluations and var not in evaluations[FALSE_ASSIGNMENTS]:
                # can't evaluate yet
                # value should not be set yet
                assert self.values == ValueStatus.NOT_SET
                return EvaluationResult.NOT_CHANGED

        evals = {}
        for c_var, var in zip(self.converted_in_vars, self.in_vars):
            evals[var] = evaluations[c_var]

        try:
            evaluator.run_stmt(self.stmt, evals, env)
        except evaluator.FailIntegrityExn as e:
            self.decision_level = ctl.assignment.decision_level
            return EvaluationResult.CONFLICT

        self.values = []
        for c_out_var, out_var in zip(self.converted_out_vars, self.out_vars):
            if out_var not in evals:
                self.values.append((c_out_var, None))
            else:
                self.values.append((c_out_var, evals[out_var]))

        return EvaluationResult.CHANGED

    def get_value(self) -> ValueStatus | list[tuple[clingo.Symbol, Any]]:
        return self.values

    def add_run_literal(self, lit: int):
        self.literal = lit

    def vars(self) -> set[clingo.Symbol]:
        return set(self.converted_in_vars)

    def reset(self, dl: int):
        if self.decision_level >= dl:
            self.decision_level = sys.maxsize

            self.values = ValueStatus.NOT_SET


def make_dict_from_variables(
    variables: Sequence[VariableType],
) -> dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]:
    result: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]] = {FALSE_ASSIGNMENTS: []}
    for var in variables:
        if type(var) == Execution:
            add_execution_to_dict(var, result)
        elif type(var) in (Variable, SetVariable, DictVariable):
            add_variable_to_dict(var, result)

    return result


def add_variable_to_dict(
    var: Variable | SetVariable | DictVariable, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]
) -> None:
    value = var.get_value()

    if value == ValueStatus.NOT_SET:
        return

    elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
        d[FALSE_ASSIGNMENTS].append(var.var)

    else:
        d[var.var] = value


def add_execution_to_dict(exec: Execution, d: dict[clingo.Symbol, Any | set[Any] | dict[Any, Any]]) -> None:
    value: ValueStatus | list[tuple[clingo.Symbol, Any]] = exec.get_value()

    if value == ValueStatus.NOT_SET:
        return

    elif value == ValueStatus.ASSIGNMENT_IS_FALSE:
        for out_var in exec.converted_out_vars:
            d[FALSE_ASSIGNMENTS].append(out_var)
    else:
        for out_var, val in value:
            d[out_var] = val
