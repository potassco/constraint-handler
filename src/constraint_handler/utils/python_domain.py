from __future__ import annotations
from dataclasses import dataclass, field
from functools import cache
from itertools import product
import math
from typing import Any, Callable, ClassVar, Iterable, Mapping

import clingo
import constraint_handler.evaluator as evaluator
import constraint_handler.solver_environment as solver_environment

DomainAtom = bool | int | float | str | None | clingo.Symbol | tuple["DomainAtom", ...] | frozenset["DomainAtom"]
PYTHON_BAD = object()


def _environment_key(identifier: object) -> object:
    """Normalize solver environment identifiers for dictionary lookups."""
    if isinstance(identifier, clingo.Symbol) and identifier.type == clingo.SymbolType.Number:
        return identifier.number
    return identifier


def get_environment(identifiers: tuple[clingo.Symbol, ...]) -> dict[str, Any]:
    """Build the Python globals for one normalized solver-identifier tuple."""
    environment = dict(evaluator._shared_environment)
    exec("", environment)
    for identifier in identifiers:
        key = _environment_key(identifier)
        if key in evaluator._solver_environment:
            environment.update(evaluator._solver_environment[key])
        else:
            print(f"debug: undeclared globals for {identifier}")
    return environment


@cache
def get_compiled_eval(code: str):
    """Compile one Python expression string once."""
    return compile(code, "<string>", "eval")


@cache
def get_compiled_exec(code: str):
    """Compile one Python statement string once."""
    return compile(code, "<string>", "exec")


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """Describe how one operator should be dispatched over child domains."""

    method_name: str
    min_arity: int | None = None
    max_arity: int | None = None
    fold_identity: Callable[[type["Domain"]], "Domain"] | None = None
    seed_with_identity: bool = False
    pass_set_members: bool = False


def _identity_empty(cls: type["Domain"]) -> "Domain":
    return cls.empty()


def _identity_zero(cls: type["Domain"]) -> "Domain":
    return cls.integers(0)


def _identity_one(cls: type["Domain"]) -> "Domain":
    return cls.integers(1)


def _identity_true(cls: type["Domain"]) -> "Domain":
    return cls.booleans(True)


def _identity_false(cls: type["Domain"]) -> "Domain":
    return cls.booleans(False)


@dataclass(slots=True)
class Domain:
    """Compact domain model for compile2 without using expression wrappers.

    Set-valued domains are modeled by their candidate atoms plus either an
    explicit subset collection or ``None`` to mean that every subset of the
    candidate atoms is valid.
    """

    LOGIC_BAD: ClassVar[object] = object()
    BAD_SYMBOL: ClassVar[clingo.Symbol] = clingo.Function("bad")
    GLOBAL_SET_UIDS: ClassVar[dict[frozenset[DomainAtom], int]] = {}
    NEXT_SET_UID: ClassVar[int] = 0
    THRESHOLD_ITERATIONS_BOOLEAN_OUTPUT: ClassVar[int] = 4 * 4
    BOOLEAN_OUTPUT_OPERATORS_WITH_NONE: ClassVar[frozenset[str]] = frozenset({"lnot", "snot", "wnot"})
    OPERATION_SPECS: ClassVar[dict[str, OperationSpec]] = {
        "add": OperationSpec("op_add", fold_identity=_identity_zero),
        "mult": OperationSpec("op_mult", fold_identity=_identity_one),
        "conj": OperationSpec("op_conj", fold_identity=_identity_true),
        "disj": OperationSpec("op_disj", fold_identity=_identity_false),
        "leqv": OperationSpec("op_leqv", fold_identity=_identity_true, seed_with_identity=True),
        "lxor": OperationSpec("op_lxor", fold_identity=_identity_false, seed_with_identity=True),
        "max": OperationSpec("op_max"),
        "min": OperationSpec("op_min"),
        "set_make": OperationSpec("op_set_make"),
        "if": OperationSpec("op_if", min_arity=2, max_arity=2),
        "set_isin": OperationSpec("op_set_isin", pass_set_members=True),
        "set_notin": OperationSpec("op_set_notin", pass_set_members=True),
        "union": OperationSpec(
            "op_union",
            fold_identity=_identity_empty,
            pass_set_members=True,
        ),
        "inter": OperationSpec(
            "op_inter",
            fold_identity=_identity_empty,
            pass_set_members=True,
        ),
        "diff": OperationSpec(
            "op_diff",
            fold_identity=_identity_empty,
            pass_set_members=True,
        ),
        "subset": OperationSpec("op_subset", pass_set_members=True),
    }

    is_bad: bool = False
    bools: set[bool] = field(default_factory=set)
    ints: set[int] = field(default_factory=set)
    floats: set[float] = field(default_factory=set)
    is_none: bool = False
    strings: set[str] = field(default_factory=set)
    symbols: set[clingo.Symbol] = field(default_factory=set)
    tuples: set[tuple[DomainAtom, ...]] = field(default_factory=set)
    domain_atoms: set[DomainAtom] = field(default_factory=set)
    possible_subsets: set[frozenset[DomainAtom]] | None = field(default_factory=set)
    _sets_cache: set[frozenset[DomainAtom]] | None = field(default=None, init=False, repr=False, compare=False)
    _set_uids_cache: set[int] | None = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def empty(cls) -> Domain:
        """Return an empty domain."""
        return cls()

    @classmethod
    def bad(cls) -> Domain:
        """Return a domain containing only the bad marker."""
        return cls(is_bad=True)

    @classmethod
    def none(cls) -> Domain:
        """Return a domain containing only `none`."""
        return cls(is_none=True)

    @classmethod
    def booleans(cls, *values: bool) -> Domain:
        """Return a domain seeded with boolean values."""
        return cls(bools=set(values))

    @classmethod
    def integers(cls, *values: int) -> Domain:
        """Return a domain seeded with integer values."""
        return cls(ints=set(values))

    @classmethod
    def floats_only(cls, *values: float) -> Domain:
        """Return a domain seeded with float values."""
        return cls(floats=set(values))

    @classmethod
    def strings_only(cls, *values: str) -> Domain:
        """Return a domain seeded with string values."""
        return cls(strings=set(values))

    @classmethod
    def symbols_only(cls, *values: clingo.Symbol) -> Domain:
        """Return a domain seeded with symbol values."""
        return cls(symbols=set(values))

    @classmethod
    def tuple_values(cls, *values: tuple[DomainAtom, ...]) -> Domain:
        """Return a domain seeded with tuple values."""
        return cls(tuples=set(values))

    @classmethod
    def set_values(cls, *values: frozenset[DomainAtom]) -> Domain:
        """Return a domain seeded with concrete set values."""
        domain_atoms: set[DomainAtom] = set()
        for value in values:
            domain_atoms.update(value)
        return cls(domain_atoms=domain_atoms, possible_subsets=set(values))

    @classmethod
    def all_subsets(cls, *values: DomainAtom) -> Domain:
        """Return a domain where every subset of the candidate atoms is valid."""
        return cls(domain_atoms=set(values), possible_subsets=None)

    @classmethod
    def set_uid_sort_key(cls, value: object):
        """Build a deterministic structural ordering key for set-uid assignment."""
        if value is None:
            return (0,)
        if isinstance(value, bool):
            return (1, int(value))
        if isinstance(value, int):
            return (2, value)
        if isinstance(value, float):
            return (3, value)
        if isinstance(value, str):
            return (4, value)
        if isinstance(value, clingo.Symbol):
            return (5, value)
        if isinstance(value, tuple):
            return (6, tuple(cls.set_uid_sort_key(item) for item in value))
        if isinstance(value, frozenset):
            return (7, tuple(sorted((cls.set_uid_sort_key(item) for item in value))))
        return (8, repr(value))

    @classmethod
    def set_sort_key(cls, value: frozenset[DomainAtom]):
        """Build a deterministic structural ordering key for one concrete set value."""
        return tuple(sorted(cls.set_uid_sort_key(member) for member in value))

    @classmethod
    def register_set_uid(cls, value: frozenset[DomainAtom]) -> int:
        """Assign a stable global uid to one concrete set value."""
        if value not in cls.GLOBAL_SET_UIDS:
            cls.GLOBAL_SET_UIDS[value] = cls.NEXT_SET_UID
            cls.NEXT_SET_UID += 1
        return cls.GLOBAL_SET_UIDS[value]

    @classmethod
    def from_value(cls, value: DomainAtom) -> Domain:
        """Lift one concrete runtime value into a domain."""
        if isinstance(value, bool):
            return cls.booleans(value)
        if isinstance(value, int):
            return cls.integers(value)
        if isinstance(value, float):
            return cls.floats_only(value)
        if value is None:
            return cls.none()
        if isinstance(value, str):
            return cls.strings_only(value)
        if isinstance(value, clingo.Symbol):
            return cls.symbols_only(value)
        if isinstance(value, tuple):
            return cls.tuple_values(value)
        if isinstance(value, frozenset):
            return cls.set_values(value)
        raise TypeError(f"unsupported domain value: {value!r}")

    @classmethod
    def from_symbol(cls, symbol: clingo.Symbol) -> Domain:
        """Lift one compile2 value symbol into a runtime domain."""
        if not (
            symbol.type == clingo.SymbolType.Function
            and symbol.name == "val"
            and len(symbol.arguments) == 2
        ):
            return cls.symbols_only(symbol)

        type_symbol, raw_value = symbol.arguments
        type_name = type_symbol.name
        if type_name == "bool":
            return cls.booleans(raw_value.name == "true")
        if type_name == "int":
            return cls.integers(raw_value.number)
        if type_name == "float":
            return cls.floats_only(float(raw_value.arguments[0].string))
        if type_name == "none":
            return cls.none()
        if type_name == "string":
            return cls.strings_only(raw_value.string)
        if type_name == "symbol":
            return cls.symbols_only(raw_value)
        return cls.bad()

    @classmethod
    def value_to_symbol(cls, value: DomainAtom) -> clingo.Symbol:
        """Convert one runtime domain value back into the compile2 value encoding."""
        if isinstance(value, bool):
            return clingo.Function("val", [clingo.Function("bool"), clingo.Function("true" if value else "false")])
        if isinstance(value, int):
            return clingo.Function("val", [clingo.Function("int"), clingo.Number(value)])
        if isinstance(value, float):
            return clingo.Function("val", [clingo.Function("float"), clingo.Function("float", [clingo.String(repr(value))])])
        if value is None:
            return clingo.Function("val", [clingo.Function("none"), clingo.Function("none")])
        if isinstance(value, str):
            return clingo.Function("val", [clingo.Function("string"), clingo.String(value)])
        if isinstance(value, clingo.Symbol):
            if value == cls.BAD_SYMBOL:
                return value
            return clingo.Function("val", [clingo.Function("symbol"), value])
        if isinstance(value, tuple):
            return clingo.Tuple_([cls.value_to_symbol(item) for item in value])
        if isinstance(value, (set, frozenset)):
            return clingo.Function("set", [cls._symbol_sequence(sorted(cls.value_to_symbol(item) for item in value))])
        raise TypeError(value)

    @classmethod
    def value_to_runtime(cls, value: DomainAtom) -> Any:
        """Convert one internal domain value into direct Python runtime data."""
        if value == cls.BAD_SYMBOL:
            return PYTHON_BAD
        if isinstance(value, tuple):
            return tuple(cls.value_to_runtime(item) for item in value)
        if isinstance(value, frozenset):
            return frozenset(cls.value_to_runtime(item) for item in value)
        return value

    @classmethod
    def runtime_to_value(cls, value: Any) -> DomainAtom:
        """Normalize one direct Python runtime value into the internal domain representation."""
        if value is PYTHON_BAD:
            return cls.BAD_SYMBOL
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return value
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, clingo.Symbol):
            return value
        if isinstance(value, tuple):
            return tuple(cls.runtime_to_value(item) for item in value)
        if isinstance(value, (set, frozenset)):
            return frozenset(cls.runtime_to_value(item) for item in value)
        raise TypeError(f"unsupported runtime value: {value!r}")

    @classmethod
    def _symbol_sequence(cls, items: Iterable[clingo.Symbol]) -> clingo.Symbol:
        """Encode one list of symbols as the nested tuple-list shape used in compile2."""
        result = clingo.Tuple_([])
        for item in reversed(tuple(items)):
            result = clingo.Tuple_([item, result])
        return result

    def copy(self) -> Domain:
        """Return a shallow copy with cloned mutable sets."""
        return Domain(
            is_bad=self.is_bad,
            bools=set(self.bools),
            ints=set(self.ints),
            floats=set(self.floats),
            is_none=self.is_none,
            strings=set(self.strings),
            symbols=set(self.symbols),
            tuples=set(self.tuples),
            domain_atoms=set(self.domain_atoms),
            possible_subsets=None if self.possible_subsets is None else set(self.possible_subsets),
        )

    def _invalidate_set_cache(self) -> None:
        """Clear cached derived set views after mutating set-domain state."""
        self._sets_cache = None
        self._set_uids_cache = None

    @classmethod
    def _enumerate_all_subsets(cls, values: Iterable[DomainAtom]) -> set[frozenset[DomainAtom]]:
        """Enumerate the full power set for the provided candidate atoms."""
        items = tuple(sorted(set(values), key=cls.set_uid_sort_key))
        result: set[frozenset[DomainAtom]] = set()
        for mask in range(1 << len(items)):
            members = {item for index, item in enumerate(items) if mask & (1 << index)}
            result.add(frozenset(members))
        return result

    @property
    def sets(self) -> set[frozenset[DomainAtom]]:
        """Return all concrete set values represented by this domain."""
        if self._sets_cache is None:
            if self.possible_subsets is None:
                self._sets_cache = self._enumerate_all_subsets(self.domain_atoms)
            else:
                self._sets_cache = set(self.possible_subsets)
        return set(self._sets_cache)

    @property
    def set_uids(self) -> set[int]:
        """Return cached global ids for all possible concrete set values."""
        if self._set_uids_cache is None:
            self._set_uids_cache = {
                self.register_set_uid(set_value)
                for set_value in sorted(self.sets, key=self.set_sort_key)
            }
        return set(self._set_uids_cache)

    def absorb(self, *domains: Domain) -> Domain:
        """Mutate this domain by unioning in the provided domains."""
        for domain in domains:
            self.is_bad = self.is_bad or domain.is_bad
            self.bools.update(domain.bools)
            self.ints.update(domain.ints)
            self.floats.update(domain.floats)
            self.is_none = self.is_none or domain.is_none
            self.strings.update(domain.strings)
            self.symbols.update(domain.symbols)
            self.tuples.update(domain.tuples)
            if self.possible_subsets is None or domain.possible_subsets is None:
                merged_sets = self.sets | domain.sets
                self.domain_atoms = {member for set_value in merged_sets for member in set_value}
                self.possible_subsets = merged_sets
            else:
                self.domain_atoms.update(domain.domain_atoms)
                self.possible_subsets.update(domain.possible_subsets)
            self._invalidate_set_cache()
        return self

    @classmethod
    def merge(cls, *domains: Domain) -> Domain:
        """Return one domain containing the union of all inputs."""
        return cls.empty().absorb(*domains)

    def _scalar_iter(self, *, include_bad: bool = False) -> Iterable[bool | int | float | str | None | clingo.Symbol]:
        """Yield scalar values while preserving set-style numeric deduplication."""
        yield from self.bools
        for value in self.ints:
            if value not in self.bools:
                yield value
        for value in self.floats:
            if value not in self.bools and value not in self.ints:
                yield value
        if self.is_none:
            yield None
        yield from self.strings
        yield from self.symbols
        if include_bad and self.is_bad and self.BAD_SYMBOL not in self.symbols:
            yield self.BAD_SYMBOL

    def values(self, *, include_bad: bool = False) -> Iterable[DomainAtom]:
        """Yield all concrete values represented by this domain."""
        yield from self._scalar_iter(include_bad=include_bad)
        yield from self.tuples
        yield from self.sets

    def value_set(self, *, include_bad: bool = False) -> set[DomainAtom]:
        """Materialize the represented values when set operations are required."""
        return set(self.values(include_bad=include_bad))

    def value_count(self) -> int:
        """Count concrete non-bad values without materializing a merged set."""
        count = len(self.bools)
        count += sum(1 for value in self.ints if value not in self.bools)
        count += sum(1 for value in self.floats if value not in self.bools and value not in self.ints)
        count += int(self.is_none)
        count += len(self.strings)
        count += len(self.symbols)
        count += len(self.tuples)
        count += len(self.sets)
        return count

    def expression_domain_symbols(self, expr: clingo.Symbol, *, include_set_values: bool) -> Iterable[clingo.Symbol]:
        """Yield `_se_domain/2` tuples for one expression."""
        for value in self.values():
            if not include_set_values and isinstance(value, frozenset):
                continue
            yield clingo.Tuple_([expr, self.value_to_symbol(value)])
        if self.is_bad:
            yield clingo.Tuple_([expr, clingo.Function("bad")])

    def expression_set_domain_symbols(
        self,
        expr: clingo.Symbol,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
    ) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain/2` tuples for this domain's concrete sets."""
        for set_value in self.sets:
            uid = self.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
            yield clingo.Tuple_([expr, clingo.Number(uid)])

    def set_domain_value_symbols(
        self,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
        candidate_values: Iterable[DomainAtom] = (),
    ) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain/3` tuples for concrete set memberships."""
        candidate_values = tuple(candidate_values)
        for set_value in self.sets:
            uid = self.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
            members = set(set_value)
            for member in members | set(candidate_values):
                sign = clingo.Function("pos" if member in members else "neg")
                yield clingo.Tuple_([clingo.Number(uid), sign, self.value_to_symbol(member)])

    def expression_set_domain_symbol_symbols(
        self,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
    ) -> Iterable[clingo.Symbol]:
        """Yield `(Uid, SetValue)` tuples for this domain's concrete sets."""
        for set_value in self.sets:
            uid = self.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
            yield clingo.Tuple_([clingo.Number(uid), self.value_to_symbol(set_value)])

    def scalar_values(self) -> Iterable[bool | int | float | str | None | clingo.Symbol]:
        """Yield only scalar values, excluding tuples and concrete sets."""
        yield from self._scalar_iter()

    def numeric_values(self) -> Iterable[int | float]:
        """Yield numeric values while preserving int/float deduplication."""
        yield from self.ints
        for value in self.floats:
            if value not in self.ints:
                yield value

    def truth_values(self) -> Iterable[bool | None]:
        """Yield the truthy lattice used by logical operations."""
        yield from self.bools
        if self.is_none:
            yield None

    def has_values(self) -> bool:
        """Report whether this domain contains any non-bad possibility."""
        return bool(
            self.bools
            or self.ints
            or self.floats
            or self.is_none
            or self.strings
            or self.symbols
            or self.tuples
            or self.sets
        )

    def options(self) -> tuple[DomainAtom, ...]:
        """Return one stable enumeration of domain alternatives, including bad when present."""
        return tuple(sorted(self.values(include_bad=True), key=str))

    def without_none(self) -> Domain:
        """Return a copy with the optional-none branch removed."""
        result = self.copy()
        result.is_none = False
        return result

    @classmethod
    def operation_name(cls, operation: Any) -> str:
        """Normalize a symbolic operator representation to its name."""
        if isinstance(operation, str):
            return operation
        if hasattr(operation, "value"):
            return operation.value
        if isinstance(operation, clingo.Symbol) and operation.type == clingo.SymbolType.Function:
            return operation.name
        raise TypeError(f"unsupported operation: {operation!r}")

    @classmethod
    def coarse_boolean_output_domain(cls, operation: Any) -> Domain:
        """Return the old shortcut domain for expensive boolean-valued operators."""
        name = cls.operation_name(operation)
        domain = cls.booleans(True, False)
        if name in cls.BOOLEAN_OUTPUT_OPERATORS_WITH_NONE:
            domain.is_none = True
        domain.is_bad = True
        return domain

    @classmethod
    def has_boolean_output(cls, operation: Any) -> bool:
        """Report whether an operator always returns a boolean-like domain."""
        return cls.operation_name(operation) in {
            "leq",
            "lt",
            "geq",
            "gt",
            "eq",
            "neq",
            "conj",
            "disj",
            "leqv",
            "limp",
            "lnot",
            "lxor",
            "snot",
            "wnot",
            "hasValue",
            "set_isin",
            "set_notin",
            "subset",
        }

    @classmethod
    def operation_spec(cls, operation: Any) -> OperationSpec:
        """Return the uniform dispatch spec for one non-Python operator."""
        name = cls.operation_name(operation)
        return cls.OPERATION_SPECS.get(name, OperationSpec(f"op_{name}"))

    @classmethod
    def from_runtime(cls, value: Any) -> Domain:
        """Lift one direct Python runtime result into a domain."""
        try:
            return cls.from_value(cls.runtime_to_value(value))
        except Exception:
            return cls.bad()

    @classmethod
    def evaluate_python_expression(cls, code: str, solver_identifiers: tuple[clingo.Symbol, ...]) -> Domain:
        """Evaluate one bare Python expression as a singleton domain."""
        try:
            result = eval(get_compiled_eval(code), get_environment(solver_identifiers), {})
        except Exception:
            return cls.bad()
        return cls.from_runtime(result)

    @classmethod
    def evaluate_python_callable(
        cls,
        code: str,
        domains: tuple[Domain, ...],
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> Domain:
        """Evaluate one Python callable over the Cartesian product of child domains."""
        arg_options = [domain.options() for domain in domains]
        if any(not options for options in arg_options):
            return cls.empty()

        result = cls.empty()
        try:
            call = eval(get_compiled_eval(code), get_environment(solver_identifiers), {})
        except Exception:
            return cls.bad()

        for arg_values in product(*arg_options):
            runtime_args = tuple(cls.value_to_runtime(value) for value in arg_values)
            try:
                applied = call(*runtime_args)
            except Exception:
                result.is_none = True
                continue
            result.absorb(cls.from_runtime(applied))
        return result

    @classmethod
    def evaluate_python_extract(
        cls,
        stmt: str,
        expr_code: str,
        domains: tuple[Domain, ...],
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> Domain:
        """Evaluate one PythonExtract operator over the Cartesian product of child domains."""
        arg_options = [domain.options() for domain in domains]
        if any(not options for options in arg_options):
            return cls.empty()

        result = cls.empty()
        for arg_values in product(*arg_options):
            runtime_args = tuple(cls.value_to_runtime(value) for value in arg_values)
            try:
                locals_env = {name: val for name, val in runtime_args}
            except (TypeError, ValueError):
                result.is_bad = True
                continue
            if any(value is PYTHON_BAD for value in locals_env.values()):
                result.is_bad = True
                continue
            try:
                exec(get_compiled_exec(stmt), get_environment(solver_identifiers), locals_env)
                succeeds = True
            except solver_environment.FailIntegrityExn:
                succeeds = False
            except Exception:
                result.is_bad = True
                continue
            if expr_code == "__succeeds":
                result.bools.add(succeeds)
                continue
            try:
                result_value = eval(get_compiled_eval(expr_code), get_environment(solver_identifiers), locals_env)
            except Exception:
                result.is_bad = True
                continue
            result.absorb(cls.from_runtime(result_value))
        return result

    @classmethod
    def _fold_operation(
        cls,
        domains: tuple[Domain, ...],
        spec: OperationSpec,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Fold one operator spec from either the first argument or an explicit identity."""
        if spec.fold_identity is None:
            raise ValueError(f"operation {spec.method_name} is not foldable")
        method = getattr(cls, spec.method_name)
        if spec.seed_with_identity:
            result = spec.fold_identity(cls)
            remaining = domains
        else:
            if not domains:
                return spec.fold_identity(cls)
            result = domains[0]
            remaining = domains[1:]
        for domain in remaining:
            if spec.pass_set_members:
                result = method(result, domain, set_members=set_members)
            else:
                result = method(result, domain)
        return result

    @classmethod
    def _apply_spec(
        cls,
        spec: OperationSpec,
        domains: tuple[Domain, ...],
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Apply one operator spec to a tuple of child domains."""
        domain_count = len(domains)
        if spec.min_arity is not None and domain_count < spec.min_arity:
            raise ValueError(f"expected at least {spec.min_arity} domains, got {domain_count}")
        if spec.max_arity is not None and domain_count > spec.max_arity:
            raise ValueError(f"expected at most {spec.max_arity} domains, got {domain_count}")
        if spec.fold_identity is not None:
            return cls._fold_operation(domains, spec, set_members=set_members)
        method = getattr(cls, spec.method_name)
        if spec.pass_set_members:
            return method(*domains, set_members=set_members)
        if spec.method_name == "op_if":
            return method(*domains, cls.empty())
        return method(*domains)

    @classmethod
    def compute_domain(
        cls,
        operation: clingo.Symbol,
        *domains: Domain,
        solver_identifiers: tuple[clingo.Symbol, ...] = (),
    ) -> Domain:
        """Compute one operation domain from its symbolic operator and child domains."""
        if any(not domain.has_values() and not domain.is_none and not domain.is_bad for domain in domains):
            return cls.empty()
        if operation.type != clingo.SymbolType.Function:
            return cls.bad()
        if operation.name == "python" and len(operation.arguments) == 1:
            return cls.evaluate_python_callable(operation.arguments[0].string, domains, solver_identifiers)
        if operation.name == "pythonExtract" and len(operation.arguments) == 2:
            return cls.evaluate_python_extract(
                operation.arguments[0].string,
                operation.arguments[1].string,
                domains,
                solver_identifiers,
            )
        if cls.has_boolean_output(operation):
            apply_total = 1
            for domain in domains:
                apply_total *= domain.value_count() + int(domain.is_bad)
            if apply_total > cls.THRESHOLD_ITERATIONS_BOOLEAN_OUTPUT:
                return cls.coarse_boolean_output_domain(operation)
        try:
            return cls.apply(operation, *domains)
        except Exception:
            return cls.bad()

    @classmethod
    def apply(
        cls,
        operation: Any,
        *domains: Domain,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Dispatch one operator name to the matching domain transfer function."""
        spec = cls.operation_spec(operation)
        method = getattr(cls, spec.method_name, None)
        if method is None:
            raise NotImplementedError(cls.operation_name(operation))
        return cls._apply_spec(spec, domains, set_members=set_members)

    @classmethod
    def _resolve_sets(
        cls,
        domain: Domain,
        set_members: Mapping[int, frozenset[DomainAtom]] | None,
    ) -> set[frozenset[DomainAtom]]:
        """Return the concrete sets represented by one domain."""
        del set_members
        return domain.sets

    @classmethod
    def _has_nonset_values(cls, domain: Domain) -> bool:
        """Report whether a domain contains any concrete value that is not a set."""
        return bool(
            domain.bools
            or domain.ints
            or domain.floats
            or domain.is_none
            or domain.strings
            or domain.symbols
            or domain.tuples
        )

    @classmethod
    def _bool_domain(cls, values: set[bool], is_bad: bool = False, is_none: bool = False) -> Domain:
        """Build a boolean domain with explicit flags."""
        return cls(is_bad=is_bad, bools=set(values), is_none=is_none)

    @classmethod
    def _logic_values(cls, domain: Domain) -> tuple[object, ...]:
        """Return the abstract boolean lattice values represented by one domain."""
        values: list[object] = [False] * int(False in domain.bools) + [True] * int(True in domain.bools)
        if domain.is_none:
            values.append(None)
        if domain.is_bad:
            values.append(cls.LOGIC_BAD)
        return tuple(values)

    @classmethod
    def _logic_result_domain(cls, results: set[object]) -> Domain:
        """Lift abstract boolean lattice outcomes back into a domain."""
        return cls._bool_domain(
            {value for value in results if isinstance(value, bool)},
            is_bad=cls.LOGIC_BAD in results,
            is_none=None in results,
        )

    @classmethod
    def _map_numbers_unary(cls, domain: Domain, fn) -> Domain:
        """Apply one numeric unary function to all numeric values in a domain."""
        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = domain.is_bad
        for value in domain.ints:
            try:
                result = fn(value)
            except Exception:
                is_bad = True
                continue
            if isinstance(result, bool):
                ints.add(int(result))
            elif isinstance(result, int):
                ints.add(result)
            else:
                floats.add(float(result))
        for value in domain.floats:
            try:
                result = fn(value)
            except Exception:
                is_bad = True
                continue
            if isinstance(result, int) and not isinstance(result, bool):
                ints.add(result)
            else:
                floats.add(float(result))
        return cls(is_bad=is_bad, ints=ints, floats=floats)

    @classmethod
    def _map_numbers_binary(cls, left: Domain, right: Domain, fn, *, force_int: bool = False) -> Domain:
        """Apply one numeric binary function across the numeric cross-product."""
        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = left.is_bad or right.is_bad or bool(
            left.bools
            or left.is_none
            or left.strings
            or left.symbols
            or left.tuples
            or left.sets
            or right.bools
            or right.is_none
            or right.strings
            or right.symbols
            or right.tuples
            or right.sets
        )
        left_values = left.numeric_values()
        right_values = right.numeric_values()
        for left_value, right_value in product(left_values, right_values):
            try:
                result = fn(left_value, right_value)
            except Exception:
                is_bad = True
                continue
            if force_int:
                ints.add(int(result))
            elif isinstance(result, int) and not isinstance(result, bool):
                ints.add(result)
            else:
                floats.add(float(result))
        return cls(is_bad=is_bad, ints=ints, floats=floats)

    @classmethod
    def _compare(cls, left: Domain, right: Domain, predicate, *, operation_name: str) -> Domain:
        """Apply a comparison predicate across the value cross-product."""
        values: set[bool] = set()
        is_bad = left.is_bad or right.is_bad
        for left_value, right_value in product(left.values(), right.values()):
            try:
                values.add(bool(predicate(left_value, right_value)))
            except Exception:
                is_bad = True
        return cls._bool_domain(values, is_bad=is_bad)

    @classmethod
    def _logic_binary(cls, left: Domain, right: Domain, fn, *, operation_name: str) -> Domain:
        """Apply a binary logical operator to boolean and none-valued inputs."""
        values: set[bool] = set()
        is_bad = left.is_bad or right.is_bad
        is_none = False
        for left_value, right_value in product(left.truth_values(), right.truth_values()):
            if left_value is None or right_value is None:
                is_none = True
                continue
            values.add(fn(left_value, right_value))
        return cls._bool_domain(values, is_bad=is_bad, is_none=is_none)

    @classmethod
    def _logic_unary(cls, domain: Domain, fn, *, operation_name: str) -> Domain:
        """Apply a unary logical operator to boolean values."""
        values: set[bool] = set()
        for value in domain.bools:
            values.add(fn(value))
        return cls._bool_domain(values, is_bad=domain.is_bad, is_none=domain.is_none)

    @classmethod
    def _logic_conj(cls, left_value: object, right_value: object) -> object:
        """Evaluate conjunction on the abstract boolean lattice."""
        if left_value is False or right_value is False:
            return False
        if left_value is None or right_value is None:
            return None
        if left_value is cls.LOGIC_BAD or right_value is cls.LOGIC_BAD:
            return cls.LOGIC_BAD
        return True

    @classmethod
    def _logic_disj(cls, left_value: object, right_value: object) -> object:
        """Evaluate disjunction on the abstract boolean lattice."""
        if left_value is True or right_value is True:
            return True
        if left_value is None or right_value is None:
            return None
        if left_value is cls.LOGIC_BAD or right_value is cls.LOGIC_BAD:
            return cls.LOGIC_BAD
        return False

    @classmethod
    def _logic_limp(cls, left_value: object, right_value: object) -> object:
        """Evaluate implication on the abstract boolean lattice."""
        if left_value is False or left_value is None:
            return True
        if right_value is True:
            return True
        if left_value is cls.LOGIC_BAD or right_value is cls.LOGIC_BAD:
            return cls.LOGIC_BAD
        return right_value

    @classmethod
    def op_abs(cls, domain: Domain) -> Domain:
        """Compute the absolute-value domain."""
        return cls._map_numbers_unary(domain, abs)

    @classmethod
    def op_sqrt(cls, domain: Domain) -> Domain:
        """Compute the square-root domain."""
        return cls._map_numbers_unary(domain, math.sqrt)

    @classmethod
    def op_cos(cls, domain: Domain) -> Domain:
        """Compute the cosine domain."""
        return cls._map_numbers_unary(domain, math.cos)

    @classmethod
    def op_sin(cls, domain: Domain) -> Domain:
        """Compute the sine domain."""
        return cls._map_numbers_unary(domain, math.sin)

    @classmethod
    def op_tan(cls, domain: Domain) -> Domain:
        """Compute the tangent domain."""
        return cls._map_numbers_unary(domain, math.tan)

    @classmethod
    def op_acos(cls, domain: Domain) -> Domain:
        """Compute the arccosine domain."""
        return cls._map_numbers_unary(domain, math.acos)

    @classmethod
    def op_asin(cls, domain: Domain) -> Domain:
        """Compute the arcsine domain."""
        return cls._map_numbers_unary(domain, math.asin)

    @classmethod
    def op_atan(cls, domain: Domain) -> Domain:
        """Compute the arctangent domain."""
        return cls._map_numbers_unary(domain, math.atan)

    @classmethod
    def op_minus(cls, domain: Domain) -> Domain:
        """Negate all numeric values in the domain."""
        return cls._map_numbers_unary(domain, lambda value: -value)

    @classmethod
    def op_floor(cls, domain: Domain) -> Domain:
        """Apply floor to all numeric values in the domain."""
        return cls._map_numbers_unary(domain, math.floor)

    @classmethod
    def op_ceil(cls, domain: Domain) -> Domain:
        """Apply ceil to all numeric values in the domain."""
        return cls._map_numbers_unary(domain, math.ceil)

    @classmethod
    def op_add(cls, left: Domain, right: Domain) -> Domain:
        """Compute the addition domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs + rhs)

    @classmethod
    def op_sub(cls, left: Domain, right: Domain) -> Domain:
        """Compute the subtraction domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs - rhs)

    @classmethod
    def op_mult(cls, left: Domain, right: Domain) -> Domain:
        """Compute the multiplication domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs * rhs)

    @classmethod
    def op_int_div(cls, left: Domain, right: Domain) -> Domain:
        """Compute the integer-division domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs // rhs, force_int=True)

    @classmethod
    def op_float_div(cls, left: Domain, right: Domain) -> Domain:
        """Compute the floating-division domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs / rhs)

    @classmethod
    def op_pow(cls, left: Domain, right: Domain) -> Domain:
        """Compute the exponentiation domain."""
        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = left.is_bad or right.is_bad or bool(
            left.bools
            or left.is_none
            or left.strings
            or left.symbols
            or left.tuples
            or left.sets
            or right.bools
            or right.is_none
            or right.strings
            or right.symbols
            or right.tuples
            or right.sets
        )
        for left_value, right_value in product(left.numeric_values(), right.numeric_values()):
            if right_value == 0:
                ints.add(1)
                continue
            try:
                result = left_value**right_value
            except Exception:
                is_bad = True
                continue
            if isinstance(result, int) and not isinstance(result, bool):
                ints.add(result)
            else:
                floats.add(float(result))
        return cls(is_bad=is_bad, ints=ints, floats=floats)

    @classmethod
    def op_leq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the less-or-equal comparison domain."""
        return cls._compare(left, right, lambda lhs, rhs: lhs <= rhs, operation_name="leq")

    @classmethod
    def op_lt(cls, left: Domain, right: Domain) -> Domain:
        """Compute the strict-less-than comparison domain."""
        return cls._compare(left, right, lambda lhs, rhs: lhs < rhs, operation_name="lt")

    @classmethod
    def op_geq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the greater-or-equal comparison domain."""
        return cls._compare(left, right, lambda lhs, rhs: lhs >= rhs, operation_name="geq")

    @classmethod
    def op_gt(cls, left: Domain, right: Domain) -> Domain:
        """Compute the strict-greater-than comparison domain."""
        return cls._compare(left, right, lambda lhs, rhs: lhs > rhs, operation_name="gt")

    @classmethod
    def op_eq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the equality domain using overlap shortcuts."""
        left_values = left.value_set()
        right_values = right.value_set()
        shared = left_values & right_values
        if not left_values or not right_values:
            return cls._bool_domain(set(), is_bad=left.is_bad or right.is_bad)
        if shared and len(shared) == len(left_values) == len(right_values) == 1:
            return cls._bool_domain({True}, is_bad=left.is_bad or right.is_bad)
        if not shared:
            return cls._bool_domain({False}, is_bad=left.is_bad or right.is_bad)
        return cls._bool_domain({False, True}, is_bad=left.is_bad or right.is_bad)

    @classmethod
    def op_neq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the inequality domain from the equality domain."""
        equal = cls.op_eq(left, right)
        return cls._bool_domain(
            {not value for value in equal.bools},
            is_bad=equal.is_bad,
            is_none=equal.is_none,
        )

    @classmethod
    def op_conj(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-conjunction domain."""
        return cls._logic_result_domain(
            {
                cls._logic_conj(left_value, right_value)
                for left_value, right_value in product(cls._logic_values(left), cls._logic_values(right))
            }
        )

    @classmethod
    def op_disj(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-disjunction domain."""
        return cls._logic_result_domain(
            {
                cls._logic_disj(left_value, right_value)
                for left_value, right_value in product(cls._logic_values(left), cls._logic_values(right))
            }
        )

    @classmethod
    def op_ite(cls, condition: Domain, if_true: Domain, if_false: Domain) -> Domain:
        """Compute the if-then-else domain from the possible condition values."""
        result = cls.empty()
        if True in condition.bools:
            result.absorb(if_true)
        if False in condition.bools:
            result.absorb(if_false)
        if condition.is_none:
            result.is_none = True
        if condition.is_bad:
            result.is_bad = True
        return result

    @classmethod
    def op_if(cls, condition: Domain, if_true: Domain, if_false: Domain) -> Domain:
        """Compute the guarded-value domain for the two-argument `if` operator."""
        result = cls.empty()
        if True in condition.bools:
            result.absorb(if_true)
        if condition.is_none or False in condition.bools:
            result.is_none = True
        if condition.is_bad:
            result.is_bad = True
        return result

    @classmethod
    def op_leqv(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-equivalence domain."""
        return cls._logic_binary(left, right, lambda lhs, rhs: lhs == rhs, operation_name="leqv")

    @classmethod
    def op_limp(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-implication domain."""
        return cls._logic_result_domain(
            {
                cls._logic_limp(left_value, right_value)
                for left_value, right_value in product(cls._logic_values(left), cls._logic_values(right))
            }
        )

    @classmethod
    def op_lnot(cls, domain: Domain) -> Domain:
        """Compute the logical-negation domain."""
        return cls._logic_unary(domain, lambda value: not value, operation_name="lnot")

    @classmethod
    def op_lxor(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-exclusive-or domain."""
        return cls._logic_binary(left, right, lambda lhs, rhs: lhs != rhs, operation_name="lxor")

    @classmethod
    def op_snot(cls, domain: Domain) -> Domain:
        """Compute strong negation, where `none` collapses to `false`."""
        result = cls._bool_domain({not value for value in domain.bools}, is_bad=domain.is_bad)
        if domain.is_none:
            result.bools.add(False)
        return result

    @classmethod
    def op_wnot(cls, domain: Domain) -> Domain:
        """Compute weak negation, where `none` collapses to `true`."""
        result = cls._bool_domain({not value for value in domain.bools}, is_bad=domain.is_bad)
        if domain.is_none:
            result.bools.add(True)
        return result

    @classmethod
    def op_concat(cls, left: Domain, right: Domain) -> Domain:
        """Compute all string concatenations from two string domains."""
        return cls(
            is_bad=left.is_bad or right.is_bad,
            strings={lhs + rhs for lhs, rhs in product(left.strings, right.strings)},
        )

    @classmethod
    def op_length(cls, domain: Domain) -> Domain:
        """Compute lengths for strings, tuples, and concrete sets."""
        lengths = {len(value) for value in domain.strings}
        lengths.update(len(value) for value in domain.tuples)
        lengths.update(len(value) for value in domain.sets)
        has_invalid_values = bool(domain.bools or domain.ints or domain.floats or domain.is_none or domain.symbols)
        return cls(is_bad=domain.is_bad or has_invalid_values, ints=lengths)

    @classmethod
    def op_max(cls, *domains: Domain) -> Domain:
        """Compute all max results across the argument cross-product."""
        if not domains:
            return cls.empty()
        value_options = [tuple(domain.values()) for domain in domains]
        if any(not options for options in value_options):
            return cls.empty()

        result = cls.empty()
        result.is_bad = any(domain.is_bad for domain in domains)
        for arg_values in product(*value_options):
            try:
                result.absorb(cls.from_value(max(arg_values)))
            except Exception:
                result.is_bad = True
        return result

    @classmethod
    def op_min(cls, *domains: Domain) -> Domain:
        """Compute all min results across the argument cross-product."""
        if not domains:
            return cls.empty()
        value_options = [tuple(domain.values()) for domain in domains]
        if any(not options for options in value_options):
            return cls.empty()

        result = cls.empty()
        result.is_bad = any(domain.is_bad for domain in domains)
        for arg_values in product(*value_options):
            try:
                result.absorb(cls.from_value(min(arg_values)))
            except Exception:
                result.is_bad = True
        return result

    @classmethod
    def op_default(cls, primary: Domain, fallback: Domain) -> Domain:
        """Return the primary domain, falling back when it is only none-like."""
        result = primary.without_none()
        if primary.is_none:
            result.absorb(fallback)
        return result

    @classmethod
    def op_hasValue(cls, domain: Domain) -> Domain:
        """Return whether the domain can hold a concrete non-none value."""
        has_real_values = bool(
            domain.bools
            or domain.ints
            or domain.floats
            or domain.strings
            or domain.symbols
            or domain.tuples
            or domain.sets
        )
        values: set[bool] = set()
        if has_real_values:
            values.add(True)
        if domain.is_none:
            values.add(False)
        return cls._bool_domain(values, is_bad=domain.is_bad)

    @classmethod
    def op_set_make(cls, *domains: Domain) -> Domain:
        """Build all concrete sets produced by choosing one scalar from each input domain."""
        if not domains:
            return cls.set_values(frozenset())

        scalar_domains = [tuple(domain.scalar_values()) for domain in domains]
        if any(not values for values in scalar_domains):
            return cls(is_bad=any(domain.is_bad for domain in domains))

        result = cls.set_values(*(frozenset(values) for values in product(*scalar_domains)))
        result.is_bad = any(domain.is_bad for domain in domains)
        return result

    @classmethod
    def op_set_isin(
        cls,
        member: Domain,
        set_domain: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute whether scalar members can occur in candidate sets."""
        resolved_sets = cls._resolve_sets(set_domain, set_members)
        values = {
            value in set_value
            for value, set_value in product(member.values(), resolved_sets)
        }
        is_bad = member.is_bad or set_domain.is_bad or cls._has_nonset_values(set_domain)
        return cls._bool_domain(values, is_bad=is_bad)

    @classmethod
    def op_set_notin(
        cls,
        member: Domain,
        set_domain: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute whether scalar members can be absent from candidate sets."""
        isin = cls.op_set_isin(member, set_domain, set_members=set_members)
        return cls._bool_domain({not value for value in isin.bools}, is_bad=isin.is_bad)

    @classmethod
    def op_union(
        cls,
        left: Domain,
        right: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute the pairwise union of all candidate sets."""
        left_sets = cls._resolve_sets(left, set_members)
        right_sets = cls._resolve_sets(right, set_members)
        is_bad = (
            left.is_bad
            or right.is_bad
            or cls._has_nonset_values(left)
            or cls._has_nonset_values(right)
        )
        result = cls.set_values(*(lhs | rhs for lhs, rhs in product(left_sets, right_sets)))
        result.is_bad = is_bad
        return result

    @classmethod
    def op_inter(
        cls,
        left: Domain,
        right: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute the pairwise intersection of all candidate sets."""
        left_sets = cls._resolve_sets(left, set_members)
        right_sets = cls._resolve_sets(right, set_members)
        is_bad = (
            left.is_bad
            or right.is_bad
            or cls._has_nonset_values(left)
            or cls._has_nonset_values(right)
        )
        result = cls.set_values(*(lhs & rhs for lhs, rhs in product(left_sets, right_sets)))
        result.is_bad = is_bad
        return result

    @classmethod
    def op_diff(
        cls,
        left: Domain,
        right: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute the pairwise set difference of all candidate sets."""
        left_sets = cls._resolve_sets(left, set_members)
        right_sets = cls._resolve_sets(right, set_members)
        is_bad = (
            left.is_bad
            or right.is_bad
            or cls._has_nonset_values(left)
            or cls._has_nonset_values(right)
        )
        result = cls.set_values(*(lhs - rhs for lhs, rhs in product(left_sets, right_sets)))
        result.is_bad = is_bad
        return result

    @classmethod
    def op_subset(
        cls,
        left: Domain,
        right: Domain,
        *,
        set_members: Mapping[int, frozenset[DomainAtom]] | None = None,
    ) -> Domain:
        """Compute the subset relation over all candidate set pairs."""
        left_sets = cls._resolve_sets(left, set_members)
        right_sets = cls._resolve_sets(right, set_members)
        values = {lhs <= rhs for lhs, rhs in product(left_sets, right_sets)}
        is_bad = (
            left.is_bad
            or right.is_bad
            or cls._has_nonset_values(left)
            or cls._has_nonset_values(right)
        )
        return cls._bool_domain(values, is_bad=is_bad)
