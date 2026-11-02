from __future__ import annotations

import itertools
from typing import Callable, Protocol

import clingo
from clingo import Function

from flat_ch.core.domain import (
    DeclarationKind,
    ExecutionDeclare,
    Expression,
    ISetAssign,
    ISetBaseDomain,
    IValue,
    IVariableDeclare,
    IVariableDefine,
    IVariableDomain,
    ProgramInput,
    VariableDefault,
)
from flat_ch.core.serialization import SerializerProtocol
from flat_ch.core.ssa import SSA
from flat_ch.core.types import Type


class RegistrationProtocol(Protocol):
    def register(self, term: clingo.Symbol) -> clingo.Number: ...


def native_static_result() -> clingo.Symbol:
    return Function("registered_ir_ready", [])


class ProgramRegistry:
    """The core data store.

    It doesn't know about ASP syntax variations; it only stores clean IR.
    """

    def __init__(
        self,
        registration_factory: Callable[[ProgramRegistry, SerializerProtocol], RegistrationProtocol],
        serializer: SerializerProtocol,
    ) -> None:
        self.sequential_inputs: list[ProgramInput] = []
        self.serializer = serializer
        self.current_registration_id: int | None = None
        self._registration_ids = itertools.count(1)
        self._ssa = SSA()
        self._registration = registration_factory(self, serializer)

    def register(self, term: clingo.Symbol) -> clingo.Number:
        reg_id = next(self._registration_ids)
        self.current_registration_id = reg_id
        try:
            self._registration.register(term)
        finally:
            self.current_registration_id = None
        return clingo.Number(reg_id)

    def get_program_ir(self) -> list[ProgramInput]:
        declared_names = {node.name for node in self.sequential_inputs if isinstance(node, IVariableDeclare)}
        domain_names = {node.name for node in self.sequential_inputs if isinstance(node, IVariableDomain)}
        declarations: list[ProgramInput] = []
        for node in self.sequential_inputs:
            if (
                isinstance(node, (IVariableDefine, IVariableDomain, VariableDefault))
                and node.name not in declared_names
            ):
                declarations.append(
                    IVariableDeclare(
                        node.name,
                        registration_id=node.registration_id,
                        declaration_kind=(
                            DeclarationKind.DOMAIN if node.name in domain_names else DeclarationKind.DEFINITION
                        ),
                    )
                )
        return declarations + self.sequential_inputs

    def debug_print(self, mode: str) -> None:
        program_ir = self.get_program_ir()
        print(f"[FCH IR:{mode}] declarations={len(program_ir)}")
        for decl in program_ir:
            print(f"[FCH IR:{mode}] {decl}")

    def update_var(
        self,
        name: str,
        domain_extensions: tuple[tuple[Expression, Expression], ...],
        condition: Expression = IValue(Type.BOOL, True),
        declaration_kind: DeclarationKind = DeclarationKind.DOMAIN,
    ) -> None:
        self.sequential_inputs.append(IVariableDeclare(name, condition, self.current_registration_id, declaration_kind))
        for expression, domain_condition in domain_extensions:
            self.update_domain(name, expression, domain_condition)

    def update_domain(self, name: str, expression: Expression, condition: Expression = IValue(Type.BOOL, True)) -> None:
        self.sequential_inputs.append(IVariableDomain(name, expression, condition, self.current_registration_id))

    # TODO: Resolve missing registration scoping, then route set declarations through update_var and remove this method.
    def update_set(self, name: str, condition: Expression = IValue(Type.BOOL, True)) -> None:
        self.sequential_inputs.append(IVariableDeclare(name, condition, declaration_kind=DeclarationKind.SET))

    def update_set_base_domain(
        self, name: str, expression: Expression, condition: Expression = IValue(Type.BOOL, True)
    ) -> None:
        self.sequential_inputs.append(ISetBaseDomain(name, expression, condition))

    def update_set_assign(
        self, name: str, expression: Expression, condition: Expression = IValue(Type.BOOL, True)
    ) -> None:
        self.sequential_inputs.append(ISetAssign(name, expression, condition))

    def add_execution(self, execution: ExecutionDeclare) -> None:
        """Pipes an execution block directly through SSA and appends pure IR nodes."""
        lowered_inputs: list[ProgramInput] = self._ssa.apply(execution)
        self.sequential_inputs.extend(lowered_inputs)
