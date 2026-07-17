from __future__ import annotations

from dataclasses import dataclass

from flat_ch.core.domain import FlatFact
from flat_ch.core.operators import OPERATOR_SPECS, Operator, OperatorShape


@dataclass(frozen=True)
class FlatFactSpec:
    flat_fact: FlatFact
    variables: tuple[str, ...]

    @property
    def predicate_name(self) -> str:
        return f"_fch_{self.flat_fact.value}"


@dataclass(frozen=True)
class OperatorProjectionSpec:
    operator: Operator
    shapes: tuple[OperatorShape, ...]

    @property
    def operator_name(self) -> str:
        return self.operator.flat_name

    @property
    def flat_static_fact_name(self) -> str:
        return f"op_{self.operator_name}"

    @property
    def flat_variadic_fact_name(self) -> str:
        return f"{self.flat_static_fact_name}_variadic"

    @property
    def flat_variadic_arg_fact_name(self) -> str:
        return f"{self.flat_static_fact_name}_arg"

    @property
    def static_predicate(self) -> str:
        return f"_fch_{self.flat_static_fact_name}"

    @property
    def variadic_predicate(self) -> str:
        return f"_fch_{self.flat_variadic_fact_name}"

    @property
    def variadic_arg_predicate(self) -> str:
        return f"_fch_{self.flat_variadic_arg_fact_name}"


STRUCTURAL_FACT_SPECS: tuple[FlatFactSpec, ...] = (
    FlatFactSpec(FlatFact.VARIABLE_DECLARE, ("NAME",)),
    FlatFactSpec(FlatFact.VARIABLE_DOMAIN, ("NAME", "EXPR_ID")),
    FlatFactSpec(FlatFact.VARIABLE_DEFINE, ("NAME", "EXPR_ID")),
    FlatFactSpec(FlatFact.EXPRESSION_VALUE, ("ID", "TYPE_ID", "VALUE")),
    FlatFactSpec(FlatFact.ENSURE, ("NAME", "EXPR_ID")),
    FlatFactSpec(FlatFact.EVALUATE, ("OP", "ARGS", "EXPR_ID")),
    FlatFactSpec(FlatFact.BOOL_EVALUATE, ("EXPR", "EXPR_ID")),
    FlatFactSpec(FlatFact.SET, ("NAME",)),
    FlatFactSpec(FlatFact.SET_BASE_DOMAIN, ("NAME", "EXPR_ID")),
    FlatFactSpec(FlatFact.SET_ASSIGN, ("NAME", "EXPR_ID")),
    FlatFactSpec(FlatFact.PAIR, ("ID", "KEY_EXPR_ID", "VALUE_EXPR_ID")),
    FlatFactSpec(FlatFact.OPTIMIZE_SUM, ("ID", "ELEM", "PRIO")),
    FlatFactSpec(FlatFact.OPTIMIZE_PRECISION, ("EXPR_ID", "PRIO")),
)


OPERATOR_PROJECTION_SPECS: tuple[OperatorProjectionSpec, ...] = tuple(
    OperatorProjectionSpec(operator, OPERATOR_SPECS[operator].shapes) for operator in Operator
)
