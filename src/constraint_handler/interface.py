"""Experimental staged interface for declarative constraint-handler input."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import clingo

from constraint_handler.engine import none
from constraint_handler.main import add_to_control, find_python_values
from constraint_handler.schemas.expression import Variable, constant

type Diagnostics = tuple[clingo.Symbol, ...]


class PreprocessOptions:
    """Placeholder for preprocessing options; not implemented yet."""


class Context:
    """Placeholder for context bindings; not implemented yet."""


class Query:
    """Placeholder for enforced queries; not implemented yet."""


class Preprocessor:
    def __init__(self, options: PreprocessOptions | None = None) -> None:
        if options is not None:
            raise NotImplementedError("Preprocessing options are not implemented")
        self._programs: list[str] = []

    def add(self, program: str) -> None:
        self._programs.append(program)

    def load(self, path: Path) -> None:
        self.add(path.read_text(encoding="utf-8"))

    def add_context(self, name: str, context: Context) -> None:
        raise NotImplementedError("Preparation contexts are not implemented")


@dataclass(frozen=True)
class PreparedProblem:
    declarations: tuple[str, ...]
    diagnostics: Diagnostics = ()

    @classmethod
    def from_preprocessor(cls, preprocessor: Preprocessor) -> tuple["PreparedProblem", Diagnostics]:
        control = clingo.Control(["2", "--warn=none"])
        add_to_control(control, engine=none)
        for program in preprocessor._programs:
            control.add(program)
        control.ground()
        snapshots = []
        with control.solve(yield_=True) as handle:
            for model in handle:
                atoms = model.symbols(atoms=True)
                declarations = tuple(
                    sorted(
                        str(atom)
                        for atom in atoms
                        if atom.name in {"ch_core", "ch_solve", "ch_post"}
                        and atom.arguments[0].name != "engine_request"
                    )
                )
                diagnostics = tuple(atom for atom in atoms if atom.name == "warning")
                snapshots.append(cls(declarations, diagnostics))
            result = handle.get()
        if result.interrupted or len(snapshots) != 1:
            raise ValueError("Preparation requires exactly one uninterrupted model")
        prepared = snapshots[0]
        return prepared, prepared.diagnostics

    def dump(self, path: Path) -> None:
        raise NotImplementedError("Prepared-problem serialization is not implemented")

    @classmethod
    def load(cls, path: Path) -> "PreparedProblem":
        raise NotImplementedError("Prepared-problem loading is not implemented")


@dataclass(kw_only=True)
class SolveOptions:
    model_limit: int | None = None
    show_by_default: bool = True


@dataclass
class Model:
    values: Mapping[constant, constant]
    diagnostics: Diagnostics
    optimization_value: tuple[int, ...]
    optimality_proven: bool = field(init=False, repr=False, compare=False)


class Solver:
    def __init__(self, problem: PreparedProblem, options: SolveOptions | None = None) -> None:
        self._problem = problem
        options = options or SolveOptions()
        self._model_limit = options.model_limit
        self._show_by_default = options.show_by_default
        self._visibility: dict[constant, bool] = {}

    def add_context(self, name: str, context: Context) -> None:
        raise NotImplementedError("Runtime contexts are not implemented")

    def preset(self, values: Mapping[Variable, constant]) -> None:
        raise NotImplementedError("Presets are not implemented")

    def enforce_query(self, query: Query) -> None:
        raise NotImplementedError("Enforced queries are not implemented")

    def show(self, variable: Variable) -> None:
        self._visibility[variable.arg] = True

    def hide(self, variable: Variable) -> None:
        self._visibility[variable.arg] = False

    def solve(self) -> Model | None:
        solution = None
        for model in self.enumerate():
            solution = model
        if solution is not None:
            del solution.optimality_proven
        return solution

    def enumerate(self) -> Iterator[Model]:
        control = clingo.Control([str(self._model_limit or 0), "--warn=none"])
        add_to_control(control)
        control.add("\n".join(f"{declaration}." for declaration in self._problem.declarations))
        control.ground()
        with control.solve(yield_=True) as handle:
            for model in handle:
                values = {
                    variable: value
                    for variable, value in find_python_values(model).items()
                    if self._visibility.get(variable, self._show_by_default)
                }
                diagnostics = self._problem.diagnostics + tuple(
                    atom for atom in model.symbols(atoms=True) if atom.name == "warning"
                )
                solution = Model(MappingProxyType(values), diagnostics, tuple(model.cost))
                solution.optimality_proven = model.optimality_proven
                yield solution

    def union(self) -> Model | None:
        raise NotImplementedError("Union models are not implemented")

    def intersection(self) -> Model | None:
        raise NotImplementedError("Intersection models are not implemented")

    def supremum(self) -> Model | None:
        raise NotImplementedError("Supremum models are not implemented")

    def infimum(self) -> Model | None:
        raise NotImplementedError("Infimum models are not implemented")
