from dataclasses import dataclass, field
from typing import Literal

from constraint_handler.PropagatorConstants import PROPAGATOR_CHECK_MODE_STR

type EngineName = Literal["compile", "ground", "propagator"]


@dataclass(frozen=True)
class Engine:
    name: EngineName
    parameters: dict[str, bool] = field(default_factory=dict)

    def identifier(self) -> str:
        return "-".join((self.name, *(f"{name}={value}" for name, value in sorted(self.parameters.items()))))

    def program(self) -> str:
        program = f"engine_default({self.name})."
        if self.parameters.get("check_mode"):
            program += f"\n{PROPAGATOR_CHECK_MODE_STR}."
        return program


compile = Engine("compile")
ground = Engine("ground")
propagator = Engine("propagator")
propagator_check = Engine("propagator", {"check_mode": True})