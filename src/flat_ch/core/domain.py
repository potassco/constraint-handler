from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import TypeAlias

from clingo import Symbol

from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.types import Type


class ExprKind(IntEnum):
    VALUE = auto()
    VARIABLE = auto()
    OPERATION = auto()
    PYTHON_OPERATION = auto()
    BIND = auto()
    PAIR = auto()


class StatementKind(IntEnum):
    ASSIGN = auto()
    ASSERT = auto()
    IF = auto()
    NOOP = auto()
    PYTHON = auto()


class ProgramInputKind(IntEnum):
    VARIABLE_DECLARE = auto()
    VARIABLE_DEFINE = auto()
    ENSURE_CONSTRAINT = auto()
    EVALUATE_INPUT = auto()
    PYTHON_EVALUATE_INPUT = auto()
    BOOL_EVALUATE_INPUT = auto()
    SET_DECLARE = auto()
    OPTIMIZE_MAXIMIZE_SUM = auto()
    OPTIMIZE_PRECISION = auto()
    EXECUTION_DECLARE = auto()
    EXECUTION_RUN = auto()


class FlatFact(str, Enum):
    """The different flat facts that can be emitted by the flattener."""

    EXPRESSION_VALUE = "expr_val"
    EXPRESSION_VARIABLE = "expr_var"
    VARIABLE_DEFINE = "var_def"
    VARIABLE_DECLARE = "var_decl"
    VARIABLE_DOMAIN = "var_dom"
    ENSURE = "ensure"
    EVALUATE = "evaluate"
    BOOL_EVALUATE = "bool_evaluate"
    SET = "set_decl"
    SET_BASE_DOMAIN = "set_base_domain"
    SET_ASSIGN = "set_assign"
    OPTIMIZE_SUM = "optimize_sum"
    OPTIMIZE_LABEL = "optimize_label"
    OPTIMIZE_PRECISION = "optimize_precision"
    PAIR = "pair"

    @property
    def variables(self) -> tuple[str, ...]:
        return _FLAT_FACT_VARIABLE_MAP.get(self, ("ID",))


_FLAT_FACT_VARIABLE_MAP = {
    FlatFact.VARIABLE_DECLARE: ("NAME",),
    FlatFact.VARIABLE_DOMAIN: ("NAME", "EXPR_ID"),
    FlatFact.VARIABLE_DEFINE: ("NAME", "EXPR_ID"),
    FlatFact.EXPRESSION_VALUE: ("ID", "TYPE_ID", "VALUE"),
    FlatFact.EXPRESSION_VARIABLE: ("ID", "NAME"),
    FlatFact.ENSURE: ("NAME", "EXPR_ID"),
    FlatFact.EVALUATE: ("OP", "ARGS", "EXPR_ID"),
    FlatFact.BOOL_EVALUATE: ("EXPR", "EXPR_ID"),
    FlatFact.SET: ("NAME",),
    FlatFact.SET_BASE_DOMAIN: ("NAME", "EXPR_ID"),
    FlatFact.SET_ASSIGN: ("NAME", "EXPR_ID"),
    FlatFact.PAIR: ("ID", "KEY_EXPR_ID", "VALUE_EXPR_ID"),
    FlatFact.OPTIMIZE_SUM: ("ID", "ELEM", "PRIO"),
    FlatFact.OPTIMIZE_LABEL: ("LABEL", "EXPR_ID", "PRIO"),
    FlatFact.OPTIMIZE_PRECISION: ("EXPR_ID", "PRIO"),
}


ScalarValue: TypeAlias = int | float | str | bool | None
RuntimeValue: TypeAlias = ScalarValue | frozenset[ScalarValue | str]
OperationKind: TypeAlias = Operator | str


@dataclass(frozen=True, slots=True)
class IValue:
    type: Type
    value: RuntimeValue
    kind: ExprKind = ExprKind.VALUE


@dataclass(frozen=True, slots=True)
class IVariableRef:
    name: str
    kind: ExprKind = ExprKind.VARIABLE


@dataclass(frozen=True, slots=True)
class IOperation:
    operator: OperationKind
    arguments: tuple[Expression, ...] = ()
    kind: ExprKind = ExprKind.OPERATION


@dataclass(frozen=True, slots=True)
class IBind:
    name: str
    expression: Expression
    kind: ExprKind = ExprKind.BIND


@dataclass(frozen=True, slots=True)
class IPythonOperation:
    code: str
    arguments: tuple[IBind, ...] = ()
    outputs: tuple[str, ...] = ()
    kind: ExprKind = ExprKind.PYTHON_OPERATION


@dataclass(frozen=True, slots=True)
class IPair:
    key: Expression
    value: Expression
    kind: ExprKind = ExprKind.PAIR


Expression: TypeAlias = IValue | IVariableRef | IOperation | IPythonOperation | IBind | IPair


@dataclass(frozen=True, slots=True)
class IAssignStatement:
    variable: str
    expression: Expression
    kind: StatementKind = StatementKind.ASSIGN


@dataclass(frozen=True, slots=True)
class IAssertStatement:
    condition: Expression
    kind: StatementKind = StatementKind.ASSERT


@dataclass(frozen=True, slots=True)
class IIfStatement:
    condition: Expression
    then_branch: tuple[ExecutionStatement, ...]
    else_branch: tuple[ExecutionStatement, ...]
    kind: StatementKind = StatementKind.IF


@dataclass(frozen=True, slots=True)
class INoopStatement:
    kind: StatementKind = StatementKind.NOOP


@dataclass(frozen=True, slots=True)
class IPythonStatement:
    code: str
    kind: StatementKind = StatementKind.PYTHON


ExecutionStatement: TypeAlias = IAssignStatement | IAssertStatement | IIfStatement | INoopStatement | IPythonStatement


@dataclass(frozen=True, slots=True)
class IVariableDeclare:
    name: str | Symbol
    domain: tuple[Expression, ...] = ()
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.VARIABLE_DECLARE


@dataclass(frozen=True, slots=True)
class IVariableDefine:
    name: str | Symbol
    expression: Expression
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.VARIABLE_DEFINE


@dataclass(frozen=True, slots=True)
class EnsureConstraint:
    label: str | None
    expression: Expression
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.ENSURE_CONSTRAINT


@dataclass(frozen=True, slots=True)
class EvaluateInput:
    label: str | None
    operator: OperationKind
    arguments: tuple[Expression, ...]
    original_argument_tuple: Symbol | None = None
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.EVALUATE_INPUT


@dataclass(frozen=True, slots=True)
class PythonEvaluateInput:
    label: str | None
    code: str
    arguments: tuple[IBind, ...]
    outputs: tuple[str, ...] = ("__fch_result",)
    original_argument_tuple: Symbol | None = None
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.PYTHON_EVALUATE_INPUT


@dataclass(frozen=True, slots=True)
class BoolEvaluateInput:
    label: str | None
    expression: Expression
    original_expression: Symbol | None = None
    registration_id: int | None = None
    kind: ProgramInputKind = ProgramInputKind.BOOL_EVALUATE_INPUT


@dataclass(frozen=True, slots=True)
class ISetDeclare:
    name: str | Symbol
    base_domain: tuple[Expression, ...] = ()
    assignment: tuple[Expression, ...] = ()
    kind: ProgramInputKind = ProgramInputKind.SET_DECLARE


@dataclass(frozen=True, slots=True)
class OptimizeMaximizeSum:
    expression: Expression
    element: str | Symbol
    priority: int
    label: str | None = None
    kind: ProgramInputKind = ProgramInputKind.OPTIMIZE_MAXIMIZE_SUM


@dataclass(frozen=True, slots=True)
class OptimizePrecision:
    expression: Expression
    priority: ScalarValue | str | None = None
    kind: ProgramInputKind = ProgramInputKind.OPTIMIZE_PRECISION


@dataclass(frozen=True, slots=True)
class ExecutionDeclare:
    name: str | Symbol
    statements: tuple[ExecutionStatement, ...]
    inputs: tuple[str | Symbol, ...] = ()
    outputs: tuple[str | Symbol, ...] = ()
    label: str | None = None
    kind: ProgramInputKind = ProgramInputKind.EXECUTION_DECLARE


@dataclass(frozen=True, slots=True)
class ExecutionRun:
    name: str
    target: ScalarValue | str | None = None
    kind: ProgramInputKind = ProgramInputKind.EXECUTION_RUN


ProgramInput: TypeAlias = (
    IVariableDeclare
    | IVariableDefine
    | EnsureConstraint
    | EvaluateInput
    | PythonEvaluateInput
    | BoolEvaluateInput
    | ISetDeclare
    | OptimizeMaximizeSum
    | OptimizePrecision
    | ExecutionDeclare
    | ExecutionRun
)
