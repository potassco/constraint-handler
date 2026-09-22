from dataclasses import dataclass, field

from constraint_handler.PropagatorConstants import PROPAGATOR_CHECK_MODE_STR


@dataclass(frozen=True)
class Engine:
    name: str
    parameters: dict[str, bool] = field(default_factory=dict)

    def identifier(self) -> str:
        return "-".join((self.name, *(f"{name}={value}" for name, value in sorted(self.parameters.items()))))

    def program(self) -> str:
        program = f"engine_default({self.name})."
        if self.parameters.get("check_mode"):
            program += f"\n{PROPAGATOR_CHECK_MODE_STR}."
        return program


compile = Engine("compile")
compile2 = Engine("compile2")
fch = Engine("fch")
ground = Engine("ground")
none = Engine("none")
propagator = Engine("propagator")
propagator_check = Engine("propagator", {"check_mode": True})
