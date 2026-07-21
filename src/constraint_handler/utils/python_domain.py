from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from functools import cache
from itertools import product
from typing import Any, Callable, ClassVar, Iterable, Mapping

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.solver_environment as solver_environment

DomainAtom = bool | int | float | str | None | clingo.Symbol | tuple["DomainAtom", ...] | frozenset["DomainAtom"]
PythonExtractExecution = tuple[dict[str, Any] | None, tuple[str, ...], bool | None]
PYTHON_BAD = object()


@dataclass(frozen=True, slots=True)
class PythonEvaluationOutputRequest:
    """Describe one requested Python output for a concrete input assignment."""

    output_id: object = None
    expr_code: str | None = None


class PythonEvaluationSession:
    """Bidirectional interface used while enumerating Python evaluation traces."""

    def output_requests(self) -> tuple[PythonEvaluationOutputRequest, ...]:
        """Return the outputs the current Python evaluation should produce."""
        return (PythonEvaluationOutputRequest(),)

    def record_output(
        self,
        output_id: object,
        arg_values: tuple[DomainAtom, ...],
        assignment_domain: "Domain",
        error_messages: tuple[str, ...],
    ) -> None:
        """Receive one concrete Python output for the current assignment."""
        del output_id, arg_values, assignment_domain, error_messages


@cache
def get_environment(identifiers: tuple[clingo.Symbol, ...]) -> dict[str, Any]:
    """Build the Python globals for one normalized solver-identifier tuple."""
    environment = dict(evaluator._shared_environment)
    exec("", environment)
    for identifier in identifiers:
        key = (
            identifier.number
            if isinstance(identifier, clingo.Symbol) and identifier.type == clingo.SymbolType.Number
            else identifier
        )
        if key in evaluator._solver_environment:
            environment.update(evaluator._solver_environment[key])
    return environment


@cache
def get_compiled_eval(code: str):
    """Compile one Python expression string once."""
    return compile(code, "<string>", "eval")


@cache
def get_compiled_exec(code: str):
    """Compile one Python statement string once."""
    return compile(code, "<string>", "exec")


@cache
def cached_function(
    name: str,
    arguments: tuple[clingo.Symbol, ...] = (),
    positive: bool = True,
) -> clingo.Symbol:
    """Return one interned clingo function symbol for the given signature."""
    return clingo.Function(name, list(arguments), positive)


@cache
def cached_tuple(arguments: tuple[clingo.Symbol, ...]) -> clingo.Symbol:
    """Return one interned clingo tuple symbol for the provided arguments."""
    return clingo.Tuple_(list(arguments))


@cache
def cached_number(value: int) -> clingo.Symbol:
    """Return one interned clingo number symbol for the provided value."""
    return clingo.Number(value)


VAL_SYMBOL = cached_function("val")
BOOL_SYMBOL = cached_function("bool")
TRUE_SYMBOL = cached_function("true")
FALSE_SYMBOL = cached_function("false")
INT_SYMBOL = cached_function("int")
FLOAT_SYMBOL = cached_function("float")
NONE_SYMBOL = cached_function("none")
STRING_SYMBOL = cached_function("string")
SYMBOL_SYMBOL = cached_function("symbol")
SET_SYMBOL = cached_function("set")


@dataclass(frozen=True, slots=True)
class OperationSpec:
    """Describe how one operator should be dispatched over child domains."""

    method_name: str
    min_arity: int | None = None
    max_arity: int | None = None
    fold_identity: Callable[[type["Domain"]], "Domain"] | None = None
    seed_with_identity: bool = False


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


@dataclass(frozen=True)
class Domain:
    """Compact domain model for compile2 without using expression wrappers.

    Set-valued domains are modeled by their candidate atoms plus either an
    explicit subset collection or ``None`` to mean that every subset of the
    candidate atoms is valid.
    """

    LOGIC_BAD: ClassVar[object] = object()
    BAD_SYMBOL: ClassVar[clingo.Symbol] = cached_function("bad")
    GLOBAL_SET_UIDS: ClassVar[dict[frozenset[DomainAtom], int]] = {}
    NEXT_SET_UID: ClassVar[int] = 0
    THRESHOLD_ITERATIONS_BOOLEAN: ClassVar[int] = 4 * 4
    THRESHOLD_ITERATIONS_GENERAL: ClassVar[int] = 150 * 150
    BOOLEAN_OUTPUT_OPERATORS_WITH_NONE: ClassVar[frozenset[str]] = frozenset({"lnot", "snot", "wnot"})
    OPERATION_SPECS: ClassVar[dict[str, OperationSpec]] = {
        "add": OperationSpec("op_add", fold_identity=_identity_zero, seed_with_identity=True),
        "mult": OperationSpec("op_mult", fold_identity=_identity_one, seed_with_identity=True),
        "conj": OperationSpec("op_conj", fold_identity=_identity_true),
        "disj": OperationSpec("op_disj", fold_identity=_identity_false),
        "leqv": OperationSpec("op_leqv", fold_identity=_identity_true, seed_with_identity=True),
        "lxor": OperationSpec("op_lxor", fold_identity=_identity_false, seed_with_identity=True),
        "max": OperationSpec("op_max"),
        "min": OperationSpec("op_min"),
        "set_make": OperationSpec("op_set_make"),
        "if": OperationSpec("op_if", min_arity=2, max_arity=2),
        "set_isin": OperationSpec("op_set_isin"),
        "set_notin": OperationSpec("op_set_notin"),
        "union": OperationSpec(
            "op_union",
            fold_identity=_identity_empty,
        ),
        "inter": OperationSpec(
            "op_inter",
            fold_identity=_identity_empty,
        ),
        "diff": OperationSpec(
            "op_diff",
            fold_identity=_identity_empty,
        ),
        "subset": OperationSpec("op_subset"),
    }

    is_bad: bool = False
    bools: frozenset[bool] = field(default_factory=frozenset)
    ints: frozenset[int] = field(default_factory=frozenset)
    floats: frozenset[float] = field(default_factory=frozenset)
    is_none: bool = False
    strings: frozenset[str] = field(default_factory=frozenset)
    symbols: frozenset[clingo.Symbol] = field(default_factory=frozenset)
    tuples: frozenset[tuple[DomainAtom, ...]] = field(default_factory=frozenset)
    domain_atoms: frozenset[DomainAtom] = field(default_factory=frozenset)
    possible_subsets: frozenset[frozenset[DomainAtom]] | None = field(default_factory=frozenset)

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
        return cls(bools=frozenset(values))

    @classmethod
    def integers(cls, *values: int) -> Domain:
        """Return a domain seeded with integer values."""
        return cls(ints=frozenset(values))

    @classmethod
    def floats_only(cls, *values: float) -> Domain:
        """Return a domain seeded with float values."""
        return cls(floats=frozenset(values))

    @classmethod
    def strings_only(cls, *values: str) -> Domain:
        """Return a domain seeded with string values."""
        return cls(strings=frozenset(values))

    @classmethod
    def symbols_only(cls, *values: clingo.Symbol) -> Domain:
        """Return a domain seeded with symbol values."""
        return cls(symbols=frozenset(values))

    @classmethod
    def tuple_values(cls, *values: tuple[DomainAtom, ...]) -> Domain:
        """Return a domain seeded with tuple values."""
        return cls(tuples=frozenset(values))

    @classmethod
    def set_values(cls, *values: frozenset[DomainAtom]) -> Domain:
        """Return a domain seeded with concrete set values."""
        domain_atoms: set[DomainAtom] = set()
        for value in values:
            domain_atoms.update(value)
        return cls(domain_atoms=frozenset(domain_atoms), possible_subsets=frozenset(values))

    @classmethod
    def all_subsets(cls, *values: DomainAtom) -> Domain:
        """Return a domain where every subset of the candidate atoms is valid."""
        return cls(domain_atoms=frozenset(values), possible_subsets=None)

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
        if not (symbol.type == clingo.SymbolType.Function and symbol.name == "val" and len(symbol.arguments) == 2):
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
        """Convert one runtime domain value into the compile2 value encoding."""
        if isinstance(value, bool):
            return cached_function(
                VAL_SYMBOL.name,
                (BOOL_SYMBOL, TRUE_SYMBOL if value else FALSE_SYMBOL),
            )
        if isinstance(value, int):
            return cached_function(VAL_SYMBOL.name, (INT_SYMBOL, cached_number(value)))
        if isinstance(value, float):
            return cached_function(
                VAL_SYMBOL.name,
                (
                    FLOAT_SYMBOL,
                    cached_function(FLOAT_SYMBOL.name, (clingo.String(repr(value)),)),
                ),
            )
        if value is None:
            return cached_function(VAL_SYMBOL.name, (NONE_SYMBOL, NONE_SYMBOL))
        if isinstance(value, str):
            return cached_function(VAL_SYMBOL.name, (STRING_SYMBOL, clingo.String(value)))
        if isinstance(value, clingo.Symbol):
            if value == cls.BAD_SYMBOL:
                return value
            return cached_function(VAL_SYMBOL.name, (SYMBOL_SYMBOL, value))
        if isinstance(value, tuple):
            return cached_tuple(tuple(cls.value_to_symbol(item) for item in value))
        if isinstance(value, (set, frozenset)):
            return cached_function(
                SET_SYMBOL.name,
                (cls._symbol_sequence(sorted(cls.value_to_symbol(item) for item in value)),),
            )
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
        raise TypeError(f"unsupported runtime value type: {type(value).__name__}")

    @classmethod
    def _symbol_sequence(cls, items: Iterable[clingo.Symbol]) -> clingo.Symbol:
        """Encode one list of symbols as the nested tuple-list shape used in compile2."""
        result = cached_tuple(())
        for item in reversed(tuple(items)):
            result = cached_tuple((item, result))
        return result

    @classmethod
    def _accumulate_value(
        cls,
        value: DomainAtom,
        *,
        bools: set[bool],
        ints: set[int],
        floats: set[float],
        strings: set[str],
        tuples: set[tuple[DomainAtom, ...]],
    ) -> None:
        """Accumulate one scalar-or-tuple value into raw constructor buckets."""
        del cls
        if isinstance(value, bool):
            bools.add(value)
        elif isinstance(value, int):
            ints.add(value)
        elif isinstance(value, float):
            floats.add(value)
        elif isinstance(value, str):
            strings.add(value)
        elif isinstance(value, tuple):
            tuples.add(value)
        else:
            raise TypeError(value)

    @classmethod
    def _enumerate_all_subsets(cls, values: Iterable[DomainAtom]) -> frozenset[frozenset[DomainAtom]]:
        """Enumerate the full power set for the provided candidate atoms."""
        items = tuple(frozenset(values))
        result: set[frozenset[DomainAtom]] = set()
        for mask in range(1 << len(items)):
            members = {item for index, item in enumerate(items) if mask & (1 << index)}
            result.add(frozenset(members))
        return frozenset(result)

    def set_count(self) -> int:
        """Count concrete set values without materializing symbolic all-subset domains."""
        if self.possible_subsets is None:
            return pow(2, len(self.domain_atoms))
        return len(self.possible_subsets)

    def has_possible_sets(self) -> bool:
        """Report whether this domain includes any concrete or symbolic set value."""
        return self.possible_subsets is None or bool(self.possible_subsets)

    @property
    @cache
    def sets(self) -> frozenset[frozenset[DomainAtom]]:
        """Return all concrete set values represented by this domain."""
        if self.possible_subsets is None:
            return self._enumerate_all_subsets(self.domain_atoms)
        return self.possible_subsets

    @property
    @cache
    def set_uids(self) -> frozenset[int]:
        """Return cached global ids for all possible concrete set values."""
        return frozenset(self.register_set_uid(set_value) for set_value in sorted(self.sets, key=self.set_sort_key))

    @classmethod
    def merge(cls, *domains: Domain) -> Domain:
        """Return one domain containing the union of all inputs."""
        if not domains:
            return cls.empty()
        if len(domains) == 1:
            return domains[0]

        bools = frozenset(value for domain in domains for value in domain.bools)
        ints = frozenset(value for domain in domains for value in domain.ints)
        floats = frozenset(value for domain in domains for value in domain.floats)
        strings = frozenset(value for domain in domains for value in domain.strings)
        symbols = frozenset(value for domain in domains for value in domain.symbols)
        tuples = frozenset(value for domain in domains for value in domain.tuples)
        is_bad = any(domain.is_bad for domain in domains)
        is_none = any(domain.is_none for domain in domains)
        if any(domain.possible_subsets is None for domain in domains):
            possible_subsets = frozenset(set_value for domain in domains for set_value in domain.sets)
            domain_atoms = frozenset(member for set_value in possible_subsets for member in set_value)
        else:
            domain_atoms = frozenset(value for domain in domains for value in domain.domain_atoms)
            possible_subsets = frozenset(
                set_value
                for domain in domains
                for set_value in (() if domain.possible_subsets is None else domain.possible_subsets)
            )
        return cls(
            is_bad=is_bad,
            bools=bools,
            ints=ints,
            floats=floats,
            is_none=is_none,
            strings=strings,
            symbols=symbols,
            tuples=tuples,
            domain_atoms=domain_atoms,
            possible_subsets=possible_subsets,
        )

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

    def to_symbols(self, *, include_bad: bool = False, include_set_values: bool = True) -> Iterable[clingo.Symbol]:
        """Yield compile2 symbols while preserving native-value ordering and filtering."""
        for value in sorted(self.bools):
            yield self.value_to_symbol(value)
        for value in sorted(self.ints):
            if value not in self.bools:
                yield self.value_to_symbol(value)
        for value in sorted(self.floats):
            if value not in self.bools and value not in self.ints:
                yield self.value_to_symbol(value)
        if self.is_none:
            yield self.value_to_symbol(None)
        for value in sorted(self.strings):
            yield self.value_to_symbol(value)
        for value in sorted(self.symbols):
            yield self.value_to_symbol(value)
        for value in sorted(self.tuples, key=self.set_uid_sort_key):
            yield self.value_to_symbol(value)
        if include_set_values:
            for value in sorted(self.sets, key=self.set_sort_key):
                yield self.value_to_symbol(value)
        if include_bad and self.is_bad and self.BAD_SYMBOL not in self.symbols:
            yield self.BAD_SYMBOL

    def value_set(self, *, include_bad: bool = False) -> set[DomainAtom]:
        """Materialize the represented values when set operations are required."""
        return set(self.values(include_bad=include_bad))

    def value_count(self, *, include_bad: bool = False) -> int:
        """Count represented values for threshold heuristics without materializing sets."""
        count = len(self.bools)
        count += len(self.ints)
        count += len(self.floats)
        count += int(self.is_none)
        count += len(self.strings)
        count += len(self.symbols)
        count += len(self.tuples)
        count += self.set_count()
        if include_bad and self.is_bad:
            count += 1
        return count

    def expression_domain_symbols(self, expr: clingo.Symbol, *, include_set_values: bool) -> Iterable[clingo.Symbol]:
        """Yield `_se_domain/2` tuples for one expression."""
        for symbol in self.to_symbols(include_bad=True, include_set_values=include_set_values):
            yield cached_tuple((expr, symbol))

    def expression_set_domain_symbols(
        self,
        expr: clingo.Symbol,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
    ) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain/2` tuples for this domain's concrete sets."""
        for set_value in sorted(self.sets, key=self.set_sort_key):
            uid = self.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
            yield cached_tuple((expr, cached_number(uid)))

    def set_domain_value_symbols(
        self,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
        candidate_values: Iterable[DomainAtom] = (),
    ) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain/3` tuples for concrete set memberships."""
        for set_value in self.sets:
            yield from self.set_value_domain_symbols(
                set_value,
                global_set_uids=global_set_uids,
                candidate_values=candidate_values,
            )

    @classmethod
    def set_value_domain_symbols(
        cls,
        set_value: frozenset[DomainAtom],
        *,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
        candidate_values: Iterable[DomainAtom] = (),
    ) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain/3` tuples for one concrete set value."""
        uid = cls.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
        members = set(set_value)
        for member in sorted(members | set(candidate_values), key=cls.set_uid_sort_key):
            sign = cached_function("pos" if member in members else "neg")
            yield cached_tuple((cached_number(uid), sign, cls.value_to_symbol(member)))

    def expression_set_domain_symbol_symbols(
        self,
        global_set_uids: Mapping[frozenset[DomainAtom], int] | None = None,
    ) -> Iterable[clingo.Symbol]:
        """Yield `(Uid, SetValue)` tuples for this domain's concrete sets."""
        for set_value in sorted(self.sets, key=self.set_sort_key):
            uid = self.register_set_uid(set_value) if global_set_uids is None else global_set_uids[set_value]
            yield cached_tuple((cached_number(uid), self.value_to_symbol(set_value)))

    def scalar_values(self) -> Iterable[bool | int | float | str | None | clingo.Symbol]:
        """Yield only scalar values, excluding tuples and concrete sets."""
        yield from self._scalar_iter()

    def numeric_values(self) -> Iterable[int | float]:
        """Yield numeric values while preserving int/float deduplication."""
        yield from self.ints
        for value in self.floats:
            if value not in self.ints:
                yield value

    def arithmetic_values(self) -> Iterable[int | float]:
        """Yield numeric values with booleans coerced to their integer form."""
        bool_as_ints = {int(value) for value in self.bools}
        yield from bool_as_ints
        for value in self.ints:
            if value not in bool_as_ints:
                yield value
        for value in self.floats:
            if value not in self.ints and value not in bool_as_ints:
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
            or self.has_possible_sets()
        )

    def options(self) -> tuple[DomainAtom, ...]:
        """Return one stable enumeration of domain alternatives, including bad when present."""
        return tuple(sorted(self.values(include_bad=True), key=str))

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
        return cls(
            is_bad=True,
            bools=frozenset({True, False}),
            is_none=name in cls.BOOLEAN_OUTPUT_OPERATORS_WITH_NONE,
        )

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
    def evaluate_python_expression(
        cls,
        code: str,
        solver_identifiers: tuple[clingo.Symbol, ...],
        evaluation_session: PythonEvaluationSession,
    ) -> Domain:
        """Evaluate one bare Python expression and optionally expose the concrete output."""
        environment = get_environment(solver_identifiers)
        try:
            result = eval(get_compiled_eval(code), environment, {})
        except Exception as exn:
            domain = cls.bad()
            error_messages = (repr(exn),)
        else:
            domain = cls.from_runtime(result)
            error_messages = ()
        for request in evaluation_session.output_requests():
            evaluation_session.record_output(request.output_id, (), domain, error_messages)
        return domain

    @classmethod
    def evaluate_python_callable(
        cls,
        code: str,
        domains: tuple[Domain, ...],
        solver_identifiers: tuple[clingo.Symbol, ...],
        evaluation_session: PythonEvaluationSession,
    ) -> Domain:
        """Evaluate one Python callable and optionally expose per-input outputs."""
        arg_options = [domain.options() for domain in domains]
        if any(not options for options in arg_options):
            return cls.empty()

        result_domains: list[Domain] = []
        try:
            call = eval(get_compiled_eval(code), get_environment(solver_identifiers), {})
        except Exception as exn:
            call = None
            call_error_messages = (repr(exn),)
        else:
            call_error_messages = ()

        for arg_values in product(*arg_options):
            if call_error_messages:
                domain = cls.bad()
                error_messages = call_error_messages
            else:
                runtime_args = tuple(cls.value_to_runtime(value) for value in arg_values)
                try:
                    applied = call(*runtime_args)
                except Exception as exn:
                    domain = cls.bad()
                    error_messages = (repr(exn),)
                else:
                    domain = cls.from_runtime(applied)
                    error_messages = ()
            result_domains.append(domain)
            for request in evaluation_session.output_requests():
                evaluation_session.record_output(request.output_id, arg_values, domain, error_messages)
        return cls.merge(*result_domains)

    @classmethod
    def evaluate_python_extract(
        cls,
        stmt: str,
        expr_code: str,
        domains: tuple[Domain, ...],
        solver_identifiers: tuple[clingo.Symbol, ...],
        evaluation_session: PythonEvaluationSession,
    ) -> Domain:
        """Evaluate one PythonExtract operator and optionally expose per-input outputs."""
        arg_options = [domain.options() for domain in domains]
        if any(not options for options in arg_options):
            return cls.empty()

        result_domains: list[Domain] = []
        for arg_values in product(*arg_options):
            execution = cls.execute_python_extract_statement(stmt, arg_values, solver_identifiers)
            requests = evaluation_session.output_requests()
            if not requests:
                requests = (PythonEvaluationOutputRequest(expr_code=expr_code),)
            primary_domain: Domain | None = None
            for request in requests:
                requested_expr = expr_code if request.expr_code is None else request.expr_code
                domain, error_messages = cls.evaluate_python_extract_output(
                    requested_expr,
                    execution,
                )
                if primary_domain is None:
                    primary_domain = domain
                evaluation_session.record_output(request.output_id, arg_values, domain, error_messages)
            if primary_domain is not None:
                result_domains.append(primary_domain)
        return cls.merge(*result_domains)

    @classmethod
    @cache
    def execute_python_extract_statement(
        cls,
        stmt: str,
        arg_values: tuple[DomainAtom, ...],
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> PythonExtractExecution:
        """Execute one PythonExtract statement for one concrete input assignment."""
        runtime_args = tuple(cls.value_to_runtime(value) for value in arg_values)
        try:
            locals_env = {name: val for name, val in runtime_args}
        except (TypeError, ValueError):
            return None, (), None
        if any(value is PYTHON_BAD for value in locals_env.values()):
            return None, (), None
        try:
            exec(get_compiled_exec(stmt), get_environment(solver_identifiers), locals_env)
        except solver_environment.FailIntegrityExn:
            return None, (), False
        except Exception as exn:
            return None, (repr(exn),), None
        return locals_env, (), True

    @classmethod
    def evaluate_python_extract_output(
        cls,
        expr_code: str,
        execution: PythonExtractExecution,
    ) -> tuple[Domain, tuple[str, ...]]:
        """Evaluate one PythonExtract output expression against a cached statement execution."""
        locals_env, error_messages, succeeds = execution
        if locals_env is None:
            if succeeds is False and expr_code == "__succeeds":
                return cls.booleans(False), ()
            if error_messages:
                return cls.bad(), error_messages
            return cls.bad(), ()
        if expr_code == "__succeeds":
            return cls.booleans(True), ()
        if expr_code not in locals_env:
            return cls.bad(), ()
        result_value = locals_env[expr_code]
        return cls.from_runtime(result_value), ()

    @classmethod
    def _fold_operation(
        cls,
        domains: tuple[Domain, ...],
        spec: OperationSpec,
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
            result = method(result, domain)
        return result

    @classmethod
    def _apply_spec(
        cls,
        spec: OperationSpec,
        domains: tuple[Domain, ...],
    ) -> Domain:
        """Apply one operator spec to a tuple of child domains."""
        domain_count = len(domains)
        if spec.min_arity is not None and domain_count < spec.min_arity:
            raise ValueError(f"expected at least {spec.min_arity} domains, got {domain_count}")
        if spec.max_arity is not None and domain_count > spec.max_arity:
            raise ValueError(f"expected at most {spec.max_arity} domains, got {domain_count}")
        if spec.fold_identity is not None:
            return cls._fold_operation(domains, spec)
        method = getattr(cls, spec.method_name)
        if spec.method_name == "op_if":
            return method(*domains, cls.empty())
        return method(*domains)

    @classmethod
    def compute_domain(
        cls,
        operation: clingo.Symbol,
        *domains: Domain,
        solver_identifiers: tuple[clingo.Symbol, ...] = (),
        evaluation_session: PythonEvaluationSession,
    ) -> Domain:
        """Compute one operation domain from its symbolic operator and child domains."""
        result: Domain | None = None
        if any(not domain.has_values() and not domain.is_none and not domain.is_bad for domain in domains):
            result = cls.empty()
        elif operation.type != clingo.SymbolType.Function:
            result = cls.bad()
        elif operation.name == "python" and len(operation.arguments) == 1:
            result = cls.evaluate_python_callable(
                operation.arguments[0].string,
                domains,
                solver_identifiers,
                evaluation_session=evaluation_session,
            )
        elif operation.name == "pythonExtract" and len(operation.arguments) == 2:
            result = cls.evaluate_python_extract(
                operation.arguments[0].string,
                operation.arguments[1].string,
                domains,
                solver_identifiers,
                evaluation_session=evaluation_session,
            )
        elif cls.has_boolean_output(operation):
            if math.prod(domain.value_count(include_bad=True) for domain in domains) > cls.THRESHOLD_ITERATIONS_BOOLEAN:
                result = cls.coarse_boolean_output_domain(operation)
        if result is None:
            try:
                result = cls.apply(operation, *domains)
            except Exception:
                result = cls.bad()
        return result

    @classmethod
    def apply(
        cls,
        operation: Any,
        *domains: Domain,
    ) -> Domain:
        """Dispatch one operator name to the matching domain transfer function."""
        spec = cls.operation_spec(operation)
        method = getattr(cls, spec.method_name, None)
        if method is None:
            raise NotImplementedError(cls.operation_name(operation))
        return cls._apply_spec(spec, domains)

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
    def _ordered_options(cls, domain: Domain) -> tuple[DomainAtom, ...] | None:
        """Return orderable concrete options or ``None`` when no exact shortcut applies."""
        if domain.is_none or domain.symbols or domain.has_possible_sets():
            return None
        options = tuple(domain.scalar_values()) + tuple(domain.tuples)
        try:
            sorted(options)
        except TypeError:
            return None
        return options

    @classmethod
    def _ordered_compare_shortcut(cls, left: Domain, right: Domain, *, mode: str) -> Domain | None:
        """Use extrema to shortcut ordered comparisons when both sides are comparable."""
        left_options = cls._ordered_options(left)
        right_options = cls._ordered_options(right)
        if left_options is None or right_options is None:
            return None
        if not left_options or not right_options:
            return cls._bool_domain(set(), is_bad=left.is_bad or right.is_bad)
        try:
            left_min = min(left_options)
            left_max = max(left_options)
            right_min = min(right_options)
            right_max = max(right_options)
            if mode == "leq":
                if left_max <= right_min:
                    values = {True}
                elif left_min > right_max:
                    values = {False}
                else:
                    values = {False, True}
            elif mode == "lt":
                if left_max < right_min:
                    values = {True}
                elif left_min >= right_max:
                    values = {False}
                else:
                    values = {False, True}
            elif mode == "geq":
                if left_min >= right_max:
                    values = {True}
                elif left_max < right_min:
                    values = {False}
                else:
                    values = {False, True}
            elif mode == "gt":
                if left_min > right_max:
                    values = {True}
                elif left_max <= right_min:
                    values = {False}
                else:
                    values = {False, True}
            else:
                raise ValueError(mode)
        except TypeError:
            return None
        return cls._bool_domain(values, is_bad=left.is_bad or right.is_bad)

    @classmethod
    def _ordered_extremum(cls, domains: tuple[Domain, ...], *, prefer_max: bool) -> Domain | None:
        """Compute exact numeric min/max results without cross-product enumeration."""
        if not domains:
            return cls.empty()

        value_options: list[tuple[int | float, ...]] = []
        for domain in domains:
            if (
                domain.bools
                or domain.is_none
                or domain.strings
                or domain.symbols
                or domain.tuples
                or domain.has_possible_sets()
            ):
                return None
            options = tuple(domain.numeric_values())
            if not options:
                return cls.bad() if domain.is_bad else cls.empty()
            value_options.append(options)

        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = any(domain.is_bad for domain in domains)
        for index, options in enumerate(value_options):
            earlier_domains = value_options[:index]
            later_domains = value_options[index + 1 :]
            for candidate in options:
                try:
                    if prefer_max:
                        earlier_ok = all(
                            any(other < candidate for other in domain_values) for domain_values in earlier_domains
                        )
                        later_ok = all(
                            any(other <= candidate for other in domain_values) for domain_values in later_domains
                        )
                    else:
                        earlier_ok = all(
                            any(other > candidate for other in domain_values) for domain_values in earlier_domains
                        )
                        later_ok = all(
                            any(other >= candidate for other in domain_values) for domain_values in later_domains
                        )
                except TypeError:
                    return None
                if earlier_ok and later_ok:
                    if isinstance(candidate, int):
                        ints.add(candidate)
                    else:
                        floats.add(float(candidate))
        return cls(
            is_bad=is_bad,
            ints=frozenset(ints),
            floats=frozenset(floats),
        )

    @classmethod
    def _bool_domain(cls, values: set[bool], is_bad: bool = False, is_none: bool = False) -> Domain:
        """Build a boolean domain with explicit flags."""
        return cls(is_bad=is_bad, bools=frozenset(values), is_none=is_none)

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
        is_bad = domain.is_bad or bool(
            domain.bools
            or domain.is_none
            or domain.strings
            or domain.symbols
            or domain.tuples
            or domain.has_possible_sets()
        )
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
        return cls(is_bad=is_bad, ints=frozenset(ints), floats=frozenset(floats))

    @classmethod
    def _map_numbers_binary(cls, left: Domain, right: Domain, fn, *, force_int: bool = False) -> Domain:
        """Apply one numeric binary function across the numeric cross-product."""
        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = (
            left.is_bad
            or right.is_bad
            or bool(
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
        return cls(is_bad=is_bad, ints=frozenset(ints), floats=frozenset(floats))

    @classmethod
    def _map_arithmetic_binary(cls, left: Domain, right: Domain, fn) -> Domain:
        """Apply integer-style arithmetic where booleans contribute as 0/1."""
        ints: set[int] = set()
        floats: set[float] = set()
        is_bad = (
            left.is_bad
            or right.is_bad
            or bool(
                left.is_none
                or left.strings
                or left.symbols
                or left.tuples
                or left.sets
                or right.is_none
                or right.strings
                or right.symbols
                or right.tuples
                or right.sets
            )
        )
        for left_value, right_value in product(left.arithmetic_values(), right.arithmetic_values()):
            try:
                result = fn(left_value, right_value)
            except Exception:
                is_bad = True
                continue
            if isinstance(result, int) and not isinstance(result, bool):
                ints.add(result)
            else:
                floats.add(float(result))
        return cls(is_bad=is_bad, ints=frozenset(ints), floats=frozenset(floats))

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
    def _strict_bool_binary(cls, left: Domain, right: Domain, fn) -> Domain:
        """Apply a binary boolean operator where `none` is treated as a bad contributor."""
        values: set[bool] = set()
        is_bad = (
            left.is_bad
            or right.is_bad
            or bool(
                left.is_none
                or left.strings
                or left.symbols
                or left.tuples
                or left.sets
                or right.is_none
                or right.strings
                or right.symbols
                or right.tuples
                or right.sets
            )
        )
        for left_value, right_value in product(left.truth_values(), right.truth_values()):
            if left_value is None or right_value is None:
                continue
            values.add(fn(left_value, right_value))
        return cls._bool_domain(values, is_bad=is_bad)

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
        if left_value is cls.LOGIC_BAD or right_value is cls.LOGIC_BAD:
            return cls.LOGIC_BAD
        if left_value is None or right_value is None:
            return None
        return True

    @classmethod
    def _logic_disj(cls, left_value: object, right_value: object) -> object:
        """Evaluate disjunction on the abstract boolean lattice."""
        if left_value is True or right_value is True:
            return True
        if left_value is cls.LOGIC_BAD or right_value is cls.LOGIC_BAD:
            return cls.LOGIC_BAD
        if left_value is None or right_value is None:
            return None
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
        return cls._map_arithmetic_binary(left, right, lambda lhs, rhs: lhs + rhs)

    @classmethod
    def op_sub(cls, left: Domain, right: Domain) -> Domain:
        """Compute the subtraction domain."""
        return cls._map_numbers_binary(left, right, lambda lhs, rhs: lhs - rhs)

    @classmethod
    def op_mult(cls, left: Domain, right: Domain) -> Domain:
        """Compute the multiplication domain."""
        return cls._map_arithmetic_binary(left, right, lambda lhs, rhs: lhs * rhs)

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
        is_bad = False
        for left_value, right_value in product(left.values(include_bad=True), right.values(include_bad=True)):
            if right_value == 0:
                ints.add(1)
                continue
            if left_value == cls.BAD_SYMBOL or right_value == cls.BAD_SYMBOL:
                is_bad = True
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
        return cls(is_bad=is_bad, ints=frozenset(ints), floats=frozenset(floats))

    @classmethod
    def op_leq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the less-or-equal comparison domain."""
        shortcut = cls._ordered_compare_shortcut(left, right, mode="leq")
        if shortcut is not None:
            return shortcut
        return cls._compare(left, right, lambda lhs, rhs: lhs <= rhs, operation_name="leq")

    @classmethod
    def op_lt(cls, left: Domain, right: Domain) -> Domain:
        """Compute the strict-less-than comparison domain."""
        shortcut = cls._ordered_compare_shortcut(left, right, mode="lt")
        if shortcut is not None:
            return shortcut
        return cls._compare(left, right, lambda lhs, rhs: lhs < rhs, operation_name="lt")

    @classmethod
    def op_geq(cls, left: Domain, right: Domain) -> Domain:
        """Compute the greater-or-equal comparison domain."""
        shortcut = cls._ordered_compare_shortcut(left, right, mode="geq")
        if shortcut is not None:
            return shortcut
        return cls._compare(left, right, lambda lhs, rhs: lhs >= rhs, operation_name="geq")

    @classmethod
    def op_gt(cls, left: Domain, right: Domain) -> Domain:
        """Compute the strict-greater-than comparison domain."""
        shortcut = cls._ordered_compare_shortcut(left, right, mode="gt")
        if shortcut is not None:
            return shortcut
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
        selected_domains = tuple(
            domain
            for include, domain in ((True in condition.bools, if_true), (False in condition.bools, if_false))
            if include
        )
        return cls(
            is_bad=condition.is_bad or any(domain.is_bad for domain in selected_domains),
            bools=frozenset(value for domain in selected_domains for value in domain.bools),
            ints=frozenset(value for domain in selected_domains for value in domain.ints),
            floats=frozenset(value for domain in selected_domains for value in domain.floats),
            is_none=condition.is_none or any(domain.is_none for domain in selected_domains),
            strings=frozenset(value for domain in selected_domains for value in domain.strings),
            symbols=frozenset(value for domain in selected_domains for value in domain.symbols),
            tuples=frozenset(value for domain in selected_domains for value in domain.tuples),
            domain_atoms=frozenset(value for domain in selected_domains for value in domain.domain_atoms),
            possible_subsets=(
                frozenset(set_value for domain in selected_domains for set_value in domain.sets)
                if any(domain.possible_subsets is None for domain in selected_domains)
                else frozenset(
                    set_value
                    for domain in selected_domains
                    for set_value in (() if domain.possible_subsets is None else domain.possible_subsets)
                )
            ),
        )

    @classmethod
    def op_if(cls, condition: Domain, if_true: Domain, if_false: Domain) -> Domain:
        """Compute the guarded-value domain for the two-argument `if` operator."""
        selected_domains = (if_true,) if True in condition.bools else ()
        return cls(
            is_bad=condition.is_bad or any(domain.is_bad for domain in selected_domains),
            bools=frozenset(value for domain in selected_domains for value in domain.bools),
            ints=frozenset(value for domain in selected_domains for value in domain.ints),
            floats=frozenset(value for domain in selected_domains for value in domain.floats),
            is_none=condition.is_none or False in condition.bools or any(domain.is_none for domain in selected_domains),
            strings=frozenset(value for domain in selected_domains for value in domain.strings),
            symbols=frozenset(value for domain in selected_domains for value in domain.symbols),
            tuples=frozenset(value for domain in selected_domains for value in domain.tuples),
            domain_atoms=frozenset(value for domain in selected_domains for value in domain.domain_atoms),
            possible_subsets=(
                frozenset(set_value for domain in selected_domains for set_value in domain.sets)
                if any(domain.possible_subsets is None for domain in selected_domains)
                else frozenset(
                    set_value
                    for domain in selected_domains
                    for set_value in (() if domain.possible_subsets is None else domain.possible_subsets)
                )
            ),
        )

    @classmethod
    def op_leqv(cls, left: Domain, right: Domain) -> Domain:
        """Compute the logical-equivalence domain."""
        return cls._strict_bool_binary(left, right, lambda lhs, rhs: lhs == rhs)

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
        return cls._strict_bool_binary(left, right, lambda lhs, rhs: lhs != rhs)

    @classmethod
    def op_snot(cls, domain: Domain) -> Domain:
        """Compute strong negation, where `none` collapses to `false`."""
        values = {not value for value in domain.bools}
        if domain.is_none:
            values.add(False)
        return cls._bool_domain(values, is_bad=domain.is_bad)

    @classmethod
    def op_wnot(cls, domain: Domain) -> Domain:
        """Compute weak negation, where `none` collapses to `true`."""
        values = {not value for value in domain.bools}
        if domain.is_none:
            values.add(True)
        return cls._bool_domain(values, is_bad=domain.is_bad)

    @classmethod
    def op_concat(cls, left: Domain, right: Domain) -> Domain:
        """Compute all string concatenations from two string domains."""
        is_bad = (
            left.is_bad
            or right.is_bad
            or bool(
                left.bools
                or left.ints
                or left.floats
                or left.is_none
                or left.symbols
                or left.tuples
                or left.sets
                or right.bools
                or right.ints
                or right.floats
                or right.is_none
                or right.symbols
                or right.tuples
                or right.sets
            )
        )
        return cls(
            is_bad=is_bad,
            strings=frozenset(lhs + rhs for lhs, rhs in product(left.strings, right.strings)),
        )

    @classmethod
    def op_length(cls, domain: Domain) -> Domain:
        """Compute lengths for strings, tuples, and concrete sets."""
        lengths = {len(value) for value in domain.strings}
        lengths.update(len(value) for value in domain.tuples)
        if domain.possible_subsets is None or len(domain.possible_subsets) > cls.THRESHOLD_ITERATIONS_GENERAL:
            lengths.update(range(len(domain.domain_atoms) + 1))
        else:
            lengths.update(len(value) for value in domain.possible_subsets)
        has_invalid_values = bool(domain.bools or domain.ints or domain.floats or domain.is_none or domain.symbols)
        return cls(is_bad=domain.is_bad or has_invalid_values, ints=frozenset(lengths))

    @classmethod
    def _numeric_extremum_domain(cls, domains: tuple[Domain, ...], *, prefer_max: bool) -> Domain:
        """Compute min/max domain while preserving bad from non-numeric contributors."""
        if not domains:
            return cls.empty()

        is_bad = any(domain.is_bad for domain in domains)
        numeric_domains: list[Domain] = []
        for domain in domains:
            if (
                domain.bools
                or domain.is_none
                or domain.strings
                or domain.symbols
                or domain.tuples
                or domain.has_possible_sets()
            ):
                is_bad = True
            numeric_domain = cls(
                ints=domain.ints,
                floats=domain.floats,
            )
            if not numeric_domain.has_values():
                return cls.bad() if is_bad else cls.empty()
            numeric_domains.append(numeric_domain)

        shortcut = cls._ordered_extremum(tuple(numeric_domains), prefer_max=prefer_max)
        if shortcut is not None:
            return replace(shortcut, is_bad=is_bad)

        value_options = [tuple(domain.values()) for domain in numeric_domains]
        if any(not options for options in value_options):
            return cls.empty()

        ints: set[int] = set()
        floats: set[float] = set()
        extremum = max if prefer_max else min
        for arg_values in product(*value_options):
            try:
                result = extremum(arg_values)
                if isinstance(result, int) and not isinstance(result, bool):
                    ints.add(result)
                else:
                    floats.add(float(result))
            except Exception:
                is_bad = True
        return cls(
            is_bad=is_bad,
            ints=frozenset(ints),
            floats=frozenset(floats),
        )

    @classmethod
    def op_max(cls, *domains: Domain) -> Domain:
        """Compute all max results across the argument cross-product."""
        return cls._numeric_extremum_domain(domains, prefer_max=True)

    @classmethod
    def op_min(cls, *domains: Domain) -> Domain:
        """Compute all min results across the argument cross-product."""
        return cls._numeric_extremum_domain(domains, prefer_max=False)

    @classmethod
    def op_default(cls, primary: Domain, fallback: Domain) -> Domain:
        """Return the primary domain, falling back when it is only none-like."""
        if not primary.is_none:
            return replace(primary, is_none=False)
        return cls(
            is_bad=primary.is_bad or fallback.is_bad,
            bools=primary.bools | fallback.bools,
            ints=primary.ints | fallback.ints,
            floats=primary.floats | fallback.floats,
            is_none=fallback.is_none,
            strings=primary.strings | fallback.strings,
            symbols=primary.symbols | fallback.symbols,
            tuples=primary.tuples | fallback.tuples,
            domain_atoms=primary.domain_atoms | fallback.domain_atoms,
            possible_subsets=(
                frozenset(primary.sets | fallback.sets)
                if primary.possible_subsets is None or fallback.possible_subsets is None
                else primary.possible_subsets | fallback.possible_subsets
            ),
        )

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

        return replace(
            cls.set_values(*(frozenset(values) for values in product(*scalar_domains))),
            is_bad=any(domain.is_bad for domain in domains),
        )

    @classmethod
    def op_set_isin(
        cls,
        member: Domain,
        set_domain: Domain,
    ) -> Domain:
        """Compute whether scalar members can occur in candidate sets."""
        values = {value in set_value for value, set_value in product(member.values(), set_domain.sets)}
        is_bad = member.is_bad or set_domain.is_bad or cls._has_nonset_values(set_domain)
        return cls._bool_domain(values, is_bad=is_bad)

    @classmethod
    def op_set_notin(
        cls,
        member: Domain,
        set_domain: Domain,
    ) -> Domain:
        """Compute whether scalar members can be absent from candidate sets."""
        isin = cls.op_set_isin(member, set_domain)
        return cls._bool_domain({not value for value in isin.bools}, is_bad=isin.is_bad)

    @classmethod
    def op_union(
        cls,
        left: Domain,
        right: Domain,
    ) -> Domain:
        """Compute the pairwise union of all candidate sets."""
        is_bad = left.is_bad or right.is_bad or cls._has_nonset_values(left) or cls._has_nonset_values(right)
        if left.set_count() * right.set_count() > cls.THRESHOLD_ITERATIONS_GENERAL:
            return replace(cls.all_subsets(*(left.domain_atoms | right.domain_atoms)), is_bad=is_bad)
        left_sets = left.sets
        right_sets = right.sets
        return replace(cls.set_values(*(lhs | rhs for lhs, rhs in product(left_sets, right_sets))), is_bad=is_bad)

    @classmethod
    def op_inter(
        cls,
        left: Domain,
        right: Domain,
    ) -> Domain:
        """Compute the pairwise intersection of all candidate sets."""
        is_bad = left.is_bad or right.is_bad or cls._has_nonset_values(left) or cls._has_nonset_values(right)
        if left.set_count() * right.set_count() > cls.THRESHOLD_ITERATIONS_GENERAL:
            return replace(cls.all_subsets(*(left.domain_atoms & right.domain_atoms)), is_bad=is_bad)
        left_sets = left.sets
        right_sets = right.sets
        return replace(cls.set_values(*(lhs & rhs for lhs, rhs in product(left_sets, right_sets))), is_bad=is_bad)

    @classmethod
    def op_diff(
        cls,
        left: Domain,
        right: Domain,
    ) -> Domain:
        """Compute the pairwise set difference of all candidate sets."""
        is_bad = left.is_bad or right.is_bad or cls._has_nonset_values(left) or cls._has_nonset_values(right)
        if left.set_count() * right.set_count() > cls.THRESHOLD_ITERATIONS_GENERAL:
            return replace(cls.all_subsets(*left.domain_atoms), is_bad=is_bad)
        left_sets = left.sets
        right_sets = right.sets
        return replace(cls.set_values(*(lhs - rhs for lhs, rhs in product(left_sets, right_sets))), is_bad=is_bad)

    @classmethod
    def op_subset(
        cls,
        left: Domain,
        right: Domain,
    ) -> Domain:
        """Compute the subset relation over all candidate set pairs."""
        is_bad = left.is_bad or right.is_bad or cls._has_nonset_values(left) or cls._has_nonset_values(right)
        if left.set_count() * right.set_count() > cls.THRESHOLD_ITERATIONS_GENERAL:
            return cls._bool_domain({False, True}, is_bad=is_bad)
        left_sets = left.sets
        right_sets = right.sets
        values = {lhs <= rhs for lhs, rhs in product(left_sets, right_sets)}
        return cls._bool_domain(values, is_bad=is_bad)
