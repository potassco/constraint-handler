from __future__ import annotations

import itertools
from enum import Enum
from typing import Callable, Protocol

import clingo
from clingo import Function

from flat_ch.core.domain import (
    ExecutionDeclare,
    Expression,
    ISetDeclare,
    IVariableDeclare,
    ProgramInput,
)
from flat_ch.core.serialization import SerializerProtocol
from flat_ch.core.ssa import SSA


class RegistrationProtocol(Protocol):
    def register(self, term: clingo.Symbol) -> clingo.Number: ...


class RegistryKind(str, Enum):
    VARIABLE = "var"
    SET = "set"


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
        self.registry: dict[tuple[str, str], ProgramInput] = {}
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
        return list(self.registry.values()) + self.sequential_inputs

    def debug_print(self, mode: str) -> None:
        program_ir = self.get_program_ir()
        print(f"[FCH IR:{mode}] declarations={len(program_ir)}")
        for decl in program_ir:
            print(f"[FCH IR:{mode}] {decl}")

    def update_var(self, name: str, domain_extensions: tuple[Expression, ...]) -> None:
        self.sequential_inputs.append(IVariableDeclare(name, domain_extensions, self.current_registration_id))

    def update_set(
        self, name: str, base_domain: tuple[Expression, ...] = (), assignment: tuple[Expression, ...] = ()
    ) -> None:
        key = (RegistryKind.SET.value, name)
        current = self.registry.get(key)
        if current is not None and isinstance(current, ISetDeclare):
            self.registry[key] = ISetDeclare(name, current.base_domain + base_domain, current.assignment + assignment)
        else:
            self.registry[key] = ISetDeclare(name, base_domain, assignment)

    def add_execution(self, execution: ExecutionDeclare) -> None:
        """Pipes an execution block directly through SSA and appends pure IR nodes."""
        lowered_inputs: list[ProgramInput] = self._ssa.apply(execution)
        self.sequential_inputs.extend(lowered_inputs)
