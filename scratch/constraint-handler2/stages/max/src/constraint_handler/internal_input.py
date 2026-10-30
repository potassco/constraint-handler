"""Typed internal expressions and storage, without evaluation or solving."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum, auto
from types import MappingProxyType
from typing import ClassVar, assert_never

from . import python_input
from .python_input import (
    DEFAULT_PRIORITY,
    LABEL_ANONYMOUS,
    Operator,
    Python,
    VariableRef,
)


class ValueType(StrEnum):
    """Distinguish internal scalar types, including booleans and integers."""

    boolean = auto()
    integer = auto()
    real = auto()
    string = auto()
    none = auto()


@dataclass(frozen=True, slots=True)
class ValueDef:
    """Pair a scalar literal with its explicit internal type."""

    value_type: ValueType
    value: python_input.Value

    def __str__(self) -> str:
        """Format scalar literal for display."""
        if self.value_type == ValueType.string:
            return f'"{self.value}"'
        return str(self.value)


type ExprId = int
type Set = frozenset[Expr]
type Tuple = tuple[Expr, ...]
type Expr = ValueDef | VariableRef | Set | Tuple | Operation
type OperationArg = Expr | Lambda | Python


@dataclass(frozen=True, slots=True)
class Operation:
    """Store an operator and its recursively converted arguments."""

    op: Operator
    args: tuple[OperationArg, ...]
    _INFIX_OPERATORS: ClassVar[dict[Operator, str]] = {
        Operator.eq: "==",
        Operator.neq: "!=",
        Operator.add: "+",
        Operator.sub: "-",
        Operator.mult: "*",
        Operator.int_div: "//",
        Operator.real_div: "/",
        Operator.mod: "%",
        Operator.pow: "**",
        Operator.leq: "<=",
        Operator.lt: "<",
        Operator.geq: ">=",
        Operator.gt: ">",
        Operator.conj: "and",
        Operator.disj: "or",
    }

    def __str__(self) -> str:
        """Format operation in infix or prefix call form."""
        if self.op in self._INFIX_OPERATORS and len(self.args) == 2:
            left, right = (
                f"({arg})" if isinstance(arg, Operation) else str(arg)
                for arg in self.args
            )
            return f"{left} {self._INFIX_OPERATORS[self.op]} {right}"
        return f"{self.op}({', '.join(str(arg) for arg in self.args)})"


@dataclass(frozen=True, slots=True)
class Lambda:
    """Store named parameters and an internal expression body."""

    vars: tuple[VariableRef, ...]
    expr: Expr

    def __str__(self) -> str:
        """Format lambda expression for display."""
        names = ", ".join(param.name for param in self.vars)
        return f"lambda {names}: {self.expr}"


@dataclass(frozen=True, slots=True)
class VariableChoice:
    """Retain one candidate expression ID, its condition ID, and its source label."""

    value: ExprId
    condition: ExprId
    label: str


@dataclass(frozen=True, slots=True)
class VariableDefinition:
    """Retain one defining expression ID, its condition ID, and its label."""

    value: ExprId
    condition: ExprId
    label: str


@dataclass(frozen=True, slots=True)
class VariableDefault:
    """Retain a conditional default's expression IDs, priority, and label."""

    value: ExprId
    condition: ExprId
    priority: int
    label: str


@dataclass(slots=True)
class Variable:
    """Collect labeled choices, definitions, and defaults for a variable."""

    choices: list[VariableChoice] = field(default_factory=list[VariableChoice])
    definitions: list[VariableDefinition] = field(
        default_factory=list[VariableDefinition]
    )
    defaults: list[VariableDefault] = field(default_factory=list[VariableDefault])


@dataclass(slots=True)
class SetVariable:
    """Collect labeled base-domain candidates, assigned elements, and defaults for a set variable."""

    bases: list[VariableChoice] = field(default_factory=list[VariableChoice])
    assigns: list[VariableDefinition] = field(default_factory=list[VariableDefinition])
    defaults: list[VariableDefault] = field(default_factory=list[VariableDefault])


@dataclass(frozen=True, slots=True)
class Constraint:
    """Reference a labeled constraint and distinguish checks from ensures."""

    expr: ExprId
    is_check: bool
    label: str


@dataclass(frozen=True, slots=True)
class Optimization:
    """Reference a guarded integer objective with its priority and source label."""

    expr: ExprId
    condition: ExprId
    priority: int
    label: str


def convert_expression(expr: python_input.Expr) -> Expr:
    """Convert input recursively, preserving scalar types without evaluation."""
    match expr:
        case bool():
            return ValueDef(ValueType.boolean, expr)
        case int():
            return ValueDef(ValueType.integer, expr)
        case float():
            return ValueDef(ValueType.real, expr)
        case str():
            return ValueDef(ValueType.string, expr)
        case None:
            return ValueDef(ValueType.none, None)
        case VariableRef():
            return expr
        case frozenset():
            return frozenset(convert_expression(item) for item in expr)
        case tuple():
            return tuple(convert_expression(item) for item in expr)
        case python_input.Operation(op, args):
            return Operation(op, tuple(_convert_argument(arg) for arg in args))
    assert_never(expr)


def _convert_argument(arg: python_input.OperationArg) -> OperationArg:
    """Convert expression and lambda arguments while retaining Python source."""
    match arg:
        case python_input.Lambda(parameters, body):
            return Lambda(parameters, convert_expression(body))
        case Python():
            return arg
        case _:
            return convert_expression(arg)


@dataclass(slots=True)
class ConstraintStore:
    """Retain caller input as typed expressions referenced by local IDs."""

    variables: dict[VariableRef, Variable] = field(
        default_factory=dict[VariableRef, Variable], init=False
    )
    set_variables: dict[VariableRef, SetVariable] = field(
        default_factory=dict[VariableRef, SetVariable], init=False
    )
    constraints: list[Constraint] = field(default_factory=list[Constraint], init=False)
    optimizations: list[Optimization] = field(
        default_factory=list[Optimization], init=False
    )
    _expressions: dict[ExprId, Expr] = field(
        default_factory=dict[ExprId, Expr], init=False
    )

    @property
    def expressions(self) -> Mapping[ExprId, Expr]:
        """Expose stored expressions by their stable local IDs."""
        return MappingProxyType(self._expressions)

    def replace_expression(self, expr_id: ExprId, expr: Expr) -> None:
        """Replace an internal expression without changing its ID or references."""
        if expr_id not in self._expressions:
            raise KeyError(expr_id)
        self._expressions[expr_id] = expr

    def _store_expression(self, expr: python_input.Expr) -> ExprId:
        """Convert and retain an expression under a fresh store-local ID."""
        return self.add_expression(convert_expression(expr))

    def add_expression(self, expr: Expr) -> ExprId:
        """Retain an already converted expression under a fresh local ID."""
        expr_id = len(self._expressions)
        self._expressions[expr_id] = expr
        return expr_id

    def choose(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a single labeled choice to the variable, guarded by the condition."""
        choice = VariableChoice(
            self._store_expression(value),
            self._store_expression(condition),
            label,
        )
        self.variables.setdefault(name, Variable()).choices.append(choice)

    def choose_from_iterator(
        self,
        name: VariableRef,
        choices: Iterable[python_input.Expr] = (),
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Extend the variable's labeled choices, each guarded by the condition."""
        variable = self.variables.setdefault(name, Variable())
        condition_id = self._store_expression(condition)
        variable.choices.extend(
            VariableChoice(self._store_expression(expr), condition_id, label)
            for expr in choices
        )

    def define(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a labeled, conditional defining expression without evaluation."""
        definition = VariableDefinition(
            self._store_expression(value),
            self._store_expression(condition),
            label,
        )
        self.variables.setdefault(name, Variable()).definitions.append(definition)

    def default_to(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        priority: int = 0,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a labeled conditional default with the given priority."""
        default = VariableDefault(
            self._store_expression(value),
            self._store_expression(condition),
            priority,
            label,
        )
        self.variables.setdefault(name, Variable()).defaults.append(default)

    def set_contain_choose(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a candidate element to the set variable, guarded by the condition."""
        choice = VariableChoice(
            self._store_expression(value),
            self._store_expression(condition),
            label,
        )
        self.set_variables.setdefault(name, SetVariable()).bases.append(choice)

    def set_contain_choose_from_iterator(
        self,
        name: VariableRef,
        choices: Iterable[python_input.Expr] = (),
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Extend the set variable's candidate elements, each guarded by the condition."""
        variable = self.set_variables.setdefault(name, SetVariable())
        condition_id = self._store_expression(condition)
        variable.bases.extend(
            VariableChoice(self._store_expression(expr), condition_id, label)
            for expr in choices
        )

    def set_contain(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a labeled, conditional element assignment to a set variable."""
        assignment = VariableDefinition(
            self._store_expression(value),
            self._store_expression(condition),
            label,
        )
        self.set_variables.setdefault(name, SetVariable()).assigns.append(assignment)

    def set_contain_default_to(
        self,
        name: VariableRef,
        value: python_input.Expr,
        condition: python_input.Expr = True,
        priority: int = 0,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Append a labeled conditional default element with the given priority."""
        default = VariableDefault(
            self._store_expression(value),
            self._store_expression(condition),
            priority,
            label,
        )
        self.set_variables.setdefault(name, SetVariable()).defaults.append(default)

    def ensure(self, expr: python_input.Expr, label: str = LABEL_ANONYMOUS) -> None:
        """Record a mandatory constraint for later processing."""
        self.constraints.append(Constraint(self._store_expression(expr), False, label))

    def check(self, expr: python_input.Expr, label: str = LABEL_ANONYMOUS) -> None:
        """Record a diagnostic constraint for later processing."""
        self.constraints.append(Constraint(self._store_expression(expr), True, label))

    def copy(self) -> ConstraintStore:
        """Return a detached structural copy preserving store-local expression IDs."""
        clone = ConstraintStore()
        for var, variable in self.variables.items():
            clone.variables[var] = Variable(
                choices=list(variable.choices),
                definitions=list(variable.definitions),
                defaults=list(variable.defaults),
            )
        for var, set_variable in self.set_variables.items():
            clone.set_variables[var] = SetVariable(
                bases=list(set_variable.bases),
                assigns=list(set_variable.assigns),
                defaults=list(set_variable.defaults),
            )
        clone.constraints.extend(self.constraints)
        clone.optimizations.extend(self.optimizations)
        clone._expressions.update(self._expressions)
        return clone

    def merge(self, other: ConstraintStore) -> None:
        """Append all variables, set variables, and constraints from another store."""
        id_map: dict[ExprId, ExprId] = {}
        for old_id, expr in other._expressions.items():
            new_id = len(self._expressions)
            self._expressions[new_id] = expr
            id_map[old_id] = new_id
        for var, variable in other.variables.items():
            target = self.variables.setdefault(var, Variable())
            target.choices.extend(
                VariableChoice(id_map[c.value], id_map[c.condition], c.label)
                for c in variable.choices
            )
            target.definitions.extend(
                VariableDefinition(id_map[d.value], id_map[d.condition], d.label)
                for d in variable.definitions
            )
            target.defaults.extend(
                VariableDefault(
                    id_map[d.value], id_map[d.condition], d.priority, d.label
                )
                for d in variable.defaults
            )
        for var, set_variable in other.set_variables.items():
            target_set = self.set_variables.setdefault(var, SetVariable())
            target_set.bases.extend(
                VariableChoice(id_map[b.value], id_map[b.condition], b.label)
                for b in set_variable.bases
            )
            target_set.assigns.extend(
                VariableDefinition(id_map[a.value], id_map[a.condition], a.label)
                for a in set_variable.assigns
            )
            target_set.defaults.extend(
                VariableDefault(
                    id_map[d.value], id_map[d.condition], d.priority, d.label
                )
                for d in set_variable.defaults
            )
        self.constraints.extend(
            Constraint(id_map[c.expr], c.is_check, c.label) for c in other.constraints
        )
        self.optimizations.extend(
            Optimization(
                id_map[item.expr], id_map[item.condition], item.priority, item.label
            )
            for item in other.optimizations
        )

    def minimize(
        self,
        expr: python_input.Expr,
        condition: python_input.Expr = True,
        priority: int = DEFAULT_PRIORITY,
        label: str = LABEL_ANONYMOUS,
    ) -> None:
        """Minimize a guarded integer expression, with higher priorities optimized first."""
        self.optimizations.append(
            Optimization(
                self._store_expression(expr),
                self._store_expression(condition),
                priority,
                label,
            )
        )

    def __str__(self) -> str:
        """Group entries by category, one indented block per category."""
        text = "Variable choices:\n"
        for name, variable in self.variables.items():
            if variable.choices:
                text += f"  {name.name}:\n"
            for choice in variable.choices:
                condition = self._expressions[choice.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"    {{ {self._expressions[choice.value]} }}{guard}\n"
        text += "\nVariable defines:\n"
        for name, variable in self.variables.items():
            for definition in variable.definitions:
                condition = self._expressions[definition.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += (
                    f"  {name.name} = {self._expressions[definition.value]}{guard}\n"
                )
        text += "\nVariable defaults:\n"
        for name, variable in self.variables.items():
            for default in variable.defaults:
                condition = self._expressions[default.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"  {name.name} = {self._expressions[default.value]}{guard} (priority {default.priority})\n"
        text += "\nSet variable bases:\n"
        for name, set_variable in self.set_variables.items():
            if set_variable.bases:
                text += f"  {name.name}:\n"
            for base in set_variable.bases:
                condition = self._expressions[base.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"    {{ {self._expressions[base.value]} }}{guard}\n"
        text += "\nSet variable assigns:\n"
        for name, set_variable in self.set_variables.items():
            for assign in set_variable.assigns:
                condition = self._expressions[assign.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"  {name.name}: {self._expressions[assign.value]}{guard}\n"
        text += "\nSet variable defaults:\n"
        for name, set_variable in self.set_variables.items():
            for default in set_variable.defaults:
                condition = self._expressions[default.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"  {name.name}: {self._expressions[default.value]}{guard} (priority {default.priority})\n"
        text += "\nConstraints:\n"
        for c in self.constraints:
            text += (
                f"  {'check' if c.is_check else 'ensure'} {self._expressions[c.expr]}\n"
            )
        if self.optimizations:
            text += "\nOptimizations:\n"
            for item in self.optimizations:
                condition = self._expressions[item.condition]
                guard = (
                    ""
                    if condition == ValueDef(ValueType.boolean, True)
                    else f" if {condition}"
                )
                text += f"  minimize {self._expressions[item.expr]}{guard} (priority {item.priority})\n"
        return text.rstrip()
