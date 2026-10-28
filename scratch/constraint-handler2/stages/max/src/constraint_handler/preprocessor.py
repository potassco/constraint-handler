"""Preprocessing and solving workflow interface."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from types import MappingProxyType

from clingo.control import Control
from clingo.core import Library
from clingo.script import enable_python
from clingo.solve import SolveResult
from clingo.symbol import Symbol

from .asp_facts import asp_facts
from .diagnostics import Diagnostics
from .dispatching import DispatchStore, Engine, dispatch
from .domains import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    DomainStore,
    compute_domains,
)
from .internal_input import ConstraintStore
from .normalization import normalize
from .python_input import Expr, Value, VariableRef
from .splitting import DEFAULT_SUBSET_LIMIT, split
from .static_types import StaticTypeStore, compute_static_types
from .util import compute_evaluation_order


@dataclass(frozen=True, slots=True)
class PreprocessOptions:
    """Configure preprocessing of a ConstraintStore.

    continue_on_errors enables best-effort normalization, splitting, and dispatch
    despite error diagnostics. Diagnostics remain errors, ordinary operator and
    engine selection is preserved, and processing exceptions still propagate.
    """

    arguments: tuple[str, ...] = ()
    threshold: int = DEFAULT_THRESHOLD
    boolean_threshold: int = DEFAULT_BOOLEAN_THRESHOLD
    splitting_subset_limit: int = DEFAULT_SUBSET_LIMIT
    continue_on_errors: bool = False


@dataclass(frozen=True, slots=True)
class SolveOptions:
    """Configuration options for an isolated Solver session."""

    arguments: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PreparedProblem:
    """Logically immutable, shareable artifact produced by Preprocessor."""

    store: ConstraintStore
    static_types: StaticTypeStore
    domains: DomainStore
    engines: DispatchStore
    python_context: Mapping[str, object] = field(default_factory=dict)

    @property
    def asp_facts(self) -> tuple[Symbol, ...]:
        """Build the ASP fact base from the prepared store and dispatch assignments."""
        return asp_facts(
            Library(), self.store, self.engines, self.domains, self.python_context
        )

    def dump(self, path: Path) -> None:
        """Serialize this PreparedProblem to the given path."""
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path) -> PreparedProblem:
        """Load and validate a serialized PreparedProblem from the given path."""
        raise NotImplementedError

    def create_solver(self, options: SolveOptions) -> Solver:
        """Create an isolated Solver session for this prepared problem."""
        if self.engines.keys() != self.store.expressions.keys():
            raise ValueError("cannot solve a problem with preprocessing errors")
        return Solver(self, options)


class Preprocessor:
    """Prepare a ConstraintStore into a detached PreparedProblem and Diagnostics."""

    def __init__(self, options: PreprocessOptions) -> None:
        """Initialize the preprocessor with preprocessing options."""
        self._options = options
        self._store = ConstraintStore()
        self._python_context: dict[str, object] = {}

    @property
    def options(self) -> PreprocessOptions:
        """Return the preprocessing options."""
        return self._options

    def add(self, store: ConstraintStore) -> None:
        """Collect declarations and constraints from a ConstraintStore."""
        self._store.merge(store)

    def add_context(self, name: str, context: object) -> None:
        """Bind a named function or namespace for Python expressions."""
        self._python_context[name] = context

    def preprocess(self) -> tuple[PreparedProblem, Diagnostics]:
        """Snapshot, preprocess, and dispatch the store without building ASP facts."""
        snapshot = self._store.copy()
        python_context = MappingProxyType(self._python_context.copy())
        diagnostics = Diagnostics()
        order = compute_evaluation_order(snapshot, diagnostics)
        static_types = compute_static_types(snapshot, order, diagnostics)
        if self._options.continue_on_errors or not diagnostics.has_errors:
            normalize(snapshot, static_types)
            order = compute_evaluation_order(snapshot, diagnostics)
            static_types = compute_static_types(snapshot, order, diagnostics)
        domains = compute_domains(
            snapshot,
            order,
            diagnostics,
            threshold=self._options.threshold,
            boolean_threshold=self._options.boolean_threshold,
            python_context=python_context,
        )
        if self._options.continue_on_errors or not diagnostics.has_errors:
            split(
                snapshot,
                domains,
                static_types,
                order,
                diagnostics,
                subset_limit=self._options.splitting_subset_limit,
                continue_on_errors=self._options.continue_on_errors,
            )
        engines = DispatchStore()
        if self._options.continue_on_errors or not diagnostics.has_errors:
            engines = dispatch(snapshot, domains)
        return (
            PreparedProblem(
                store=snapshot,
                static_types=static_types,
                domains=domains,
                engines=engines,
                python_context=python_context,
            ),
            diagnostics,
        )


class Solver:
    """Isolated solving session created from a PreparedProblem."""

    def __init__(self, problem: PreparedProblem, options: SolveOptions) -> None:
        """Initialize an isolated solver session for the given PreparedProblem."""
        if Engine.propagator in problem.engines.values():
            raise NotImplementedError(
                "solving with unknown input domains requires a propagator"
            )
        self._problem = problem
        self._options = options
        self._library = Library()
        enable_python(self._library)
        self._control = Control(self._library, list(options.arguments))
        self._control.parse_string(
            "\n".join(
                f"{fact}."
                for fact in asp_facts(
                    self._library,
                    problem.store,
                    problem.engines,
                    problem.domains,
                    problem.python_context,
                )
            )
        )
        for encoding in (
            "native.lp",
            "none.lp",
            "boolean.lp",
            "integer.lp",
            "eq.lp",
            "set.lp",
            "tuples.lp",
            "complex.lp",
        ):
            self._control.parse_string(
                files().joinpath("encoding", encoding).read_text(encoding="utf-8"),
            )
        self._control.ground([("base", [])])

    @property
    def problem(self) -> PreparedProblem:
        """Return the PreparedProblem bound to this solver session."""
        return self._problem

    @property
    def options(self) -> SolveOptions:
        """Return the SolveOptions for this solver session."""
        return self._options

    def add_context(self, name: str, context: object) -> None:
        """Bind runtime dependencies and validate the declared interface."""
        raise NotImplementedError

    def preset(self, values: Mapping[VariableRef, Value]) -> None:
        """Preset variable values for this solver session."""
        raise NotImplementedError

    def enforce_query(self, query: Expr) -> None:
        """Enforce an additional query constraint in this solver session."""
        raise NotImplementedError

    def solve(self) -> SolveResult:
        """Solve the fact base using native declarations and complex expression rows."""
        return self._control.solve()
