from collections.abc import Iterable
from itertools import pairwise
from pathlib import Path
from typing import cast

import clingo
import pytest

from constraint_handler import add_to_control, engine, multimap
from constraint_handler.post_processor import extend_with_reasoning_mode_atoms
from constraint_handler.reasoning_modes.reasoning_modes_propagator import (
    InfimumReasoningMode,
    IntersectionReasoningMode,
    ReasoningMode,
    ReasoningModesPropagator,
    ReasoningStrategy,
    SupremumReasoningMode,
    UnionReasoningMode,
    _LatticeBound,
    _MultimapVariable,
    _PairValue,
    _ScalarVariable,
    _SetVariable,
    _Value,
)
from constraint_handler.schemas import expression


class _RecordingReasoningStrategy(ReasoningStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.models: list[dict[clingo.Symbol, object]] = []

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        self.models.append(model.copy())


class _NogoodContext:
    def __init__(self) -> None:
        self.added: list[Iterable[int]] = []

    def add_nogood(self, nogood: Iterable[int]) -> None:
        self.added.append(tuple(nogood))


class _InitRecorder:
    def __init__(self) -> None:
        self.frozen: list[int] = []
        self.clauses: list[tuple[int, ...]] = []

    def solver_literal(self, literal: int) -> int:
        return literal + 100 if literal > 0 else literal - 100

    def freeze_literal(self, literal: int) -> None:
        self.frozen.append(literal)

    def add_clause(self, clause: Iterable[int]) -> None:
        self.clauses.append(tuple(clause))


class _Model:
    def __init__(self) -> None:
        self.symbols: set[clingo.Symbol] = set()

    def extend(self, symbols) -> None:
        self.symbols.update(symbols)


def _extend(values: dict[clingo.Symbol, set[object]], mode: ReasoningMode = ReasoningMode.UNION) -> set[clingo.Symbol]:
    propagator = ReasoningModesPropagator(mode)
    propagator.reasoning_strategy.rm_model = values
    model = _Model()

    extend_with_reasoning_mode_atoms(propagator, model)

    return model.symbols


def test_extend_reasoning_mode_atoms_emits_each_scalar_value() -> None:
    variable = clingo.String("x")

    symbols = _extend({variable: {3, 5}})

    assert {symbol.name for symbol in symbols} == {"model_union"}
    assert {symbol.arguments[0] for symbol in symbols} == {variable}
    assert {symbol.arguments[1] for symbol in symbols} == {
        clingo.Function("val", [clingo.Function("int"), clingo.Number(3)]),
        clingo.Function("val", [clingo.Function("int"), clingo.Number(5)]),
    }


@pytest.mark.parametrize(
    "strategy_type, reasoning_mode, expected_value",
    [
        (SupremumReasoningMode, ReasoningMode.SUPREMUM, "TOP"),
        (InfimumReasoningMode, ReasoningMode.INFIMUM, "BOT"),
    ],
)
def test_extend_reasoning_mode_atoms_serializes_lattice_bounds_as_strings(
    strategy_type: type[ReasoningStrategy], reasoning_mode: ReasoningMode, expected_value: str
) -> None:
    variable = clingo.String("value")
    strategy = strategy_type()
    strategy.join({variable: "left"})
    strategy.join({variable: "right"})

    symbols = _extend(strategy.rm_model, reasoning_mode)

    assert symbols == {
        clingo.parse_term(f'model_{reasoning_mode.name.lower()}("value",val(string,"{expected_value}"))')
    }


def test_extend_reasoning_mode_atoms_encodes_whole_set_values() -> None:
    variable = clingo.String("items")

    symbols = _extend({variable: {frozenset({1, 2}), frozenset({3})}})

    assert symbols == {
        clingo.parse_term('model_union("items",set((val(int,1),(val(int,2),()))))'),
        clingo.parse_term('model_union("items",set((val(int,3),())))'),
    }


def test_extend_reasoning_mode_atoms_encodes_empty_set_marker() -> None:
    variable = clingo.String("items")

    symbols = _extend({variable: {frozenset()}})

    assert symbols == {clingo.parse_term('model_union("items",set(()))')}


def test_extend_reasoning_mode_atoms_encodes_whole_multimap_values() -> None:
    variable = clingo.String("mapping")
    first = multimap.Multimap.from_pairs([("key", 1), ("key", 2)])
    second = multimap.Multimap.from_pairs([("key", 3)])

    symbols = _extend({variable: {first, second}})

    assert symbols == {
        clingo.parse_term('model_union("mapping",multimap(((val(string,"key"),(val(int,1),(val(int,2),()))),()),()))'),
        clingo.parse_term('model_union("mapping",multimap(((val(string,"key"),(val(int,3),())),()),()))'),
    }


def test_extend_reasoning_mode_atoms_preserves_standard_mode_output() -> None:
    variable = clingo.String("x")

    assert _extend({variable: {3}}, ReasoningMode.STANDARD) == set()


def test_extend_reasoning_mode_atoms_encodes_empty_multimap() -> None:
    variable = clingo.String("mapping")
    value = multimap.Multimap.from_pairs([])

    assert _extend({variable: {value}}) == {clingo.parse_term('model_union("mapping",multimap((),()))')}


def test_supremum_reasoning_mode_joins_values() -> None:
    mode = SupremumReasoningMode()
    variable = clingo.String("value")

    mode.join({variable: 3})
    mode.join({variable: 7})

    assert mode.rm_model == {variable: {7}}


def test_infimum_reasoning_mode_joins_values() -> None:
    mode = InfimumReasoningMode()
    variable = clingo.String("value")

    mode.join({variable: 7})
    mode.join({variable: 3})

    assert mode.rm_model == {variable: {3}}


@pytest.mark.parametrize(
    "left, right, expected",
    [(False, False, False), (False, True, True), (True, False, True), (True, True, True)],
)
def test_supremum_reasoning_mode_joins_boolean_values(left: bool, right: bool, expected: bool) -> None:
    mode = SupremumReasoningMode()
    variable = clingo.String("value")

    mode.join({variable: left})
    mode.join({variable: right})

    assert mode.rm_model == {variable: {expected}}


@pytest.mark.parametrize(
    "left, right, expected",
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
def test_infimum_reasoning_mode_joins_boolean_values(left: bool, right: bool, expected: bool) -> None:
    mode = InfimumReasoningMode()
    variable = clingo.String("value")

    mode.join({variable: left})
    mode.join({variable: right})

    assert mode.rm_model == {variable: {expected}}


def test_supremum_and_infimum_join_set_values() -> None:
    variable = clingo.String("items")
    supremum = SupremumReasoningMode()
    infimum = InfimumReasoningMode()

    for mode in (supremum, infimum):
        mode.join({variable: frozenset({1, 2})})
        mode.join({variable: frozenset({2, 3})})

    assert supremum.rm_model == {variable: {frozenset({1, 2, 3})}}
    assert infimum.rm_model == {variable: {frozenset({2})}}


def test_supremum_and_infimum_join_multimap_values() -> None:
    variable = clingo.String("mapping")
    supremum = SupremumReasoningMode()
    infimum = InfimumReasoningMode()
    first = multimap.Multimap.from_pairs([("shared", 1), ("left", 2)])
    second = multimap.Multimap.from_pairs([("shared", 1), ("shared", 3), ("right", 4)])

    for mode in (supremum, infimum):
        mode.join({variable: first})
        mode.join({variable: second})

    expected_supremum = multimap.Multimap.from_pairs([("shared", 1), ("shared", 3), ("left", 2), ("right", 4)])
    assert supremum.rm_model == {variable: {expected_supremum}}
    assert infimum.rm_model == {variable: {multimap.Multimap.from_pairs([("shared", 1)])}}


@pytest.mark.parametrize("mode_type", [UnionReasoningMode, SupremumReasoningMode, InfimumReasoningMode])
def test_reasoning_mode_initializes_progress_witness(mode_type: type[ReasoningStrategy]) -> None:
    name = clingo.String("value")
    variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable] = {
        name: _ScalarVariable(name, [_Value(1, 1)])
    }
    mode = mode_type()
    mode.variable_lit = {name: 2}
    init = _InitRecorder()
    mode.init(cast(clingo.PropagateInit, init), variables)
    assert init.frozen == [102]
    assert init.clauses == []
    assert mode.variable_lit == {name: 2}
    assert mode.value_literals == {name: {1: 1}}


@pytest.mark.parametrize(
    "left, right, expected",
    [
        ("same", "same", "same"),
        ("TOP", "TOP", "TOP"),
        ("left", "right", _LatticeBound.TOP),
        (3, "text", _LatticeBound.TOP),
        ("text", 3, _LatticeBound.TOP),
        (True, 1, _LatticeBound.TOP),
        ("TOP", 3, _LatticeBound.TOP),
        (3, "TOP", _LatticeBound.TOP),
        ("TOP", "text", _LatticeBound.TOP),
    ],
)
def test_supremum_joins_nonnumeric_values(left: object, right: object, expected: object) -> None:
    mode = SupremumReasoningMode()
    name = clingo.String("value")
    mode.join({name: left})
    mode.join({name: right})
    assert mode.rm_model == {name: {expected}}


@pytest.mark.parametrize(
    "current, candidates, blocked",
    [
        (2, [1, 2, 3], [1, 2]),
        (2.5, [1.5, 2.5, 3.5], [1.5, 2.5]),
        (False, [False, True], [False]),
        (True, [False, True], [False, True]),
        ("same", ["same", "other", 3], ["same"]),
        (_LatticeBound.TOP, ["same", "TOP", 3], ["same", "TOP", 3]),
        ("TOP", ["same", "TOP", 3], ["TOP"]),
        (3, [2, 3, "text"], [2, 3]),
    ],
)
def test_supremum_scalar_nogoods_only_allow_improvement(
    current: object, candidates: list[object], blocked: list[object]
) -> None:
    mode = SupremumReasoningMode()
    name = clingo.String("value")
    mode.variable_lit = {name: 10}
    mode.scalar_variables = {name}
    mode.value_literals = {name: {value: literal for literal, value in enumerate(candidates, 1)}}
    mode.join({name: current})

    assert mode.nogoods() == [(mode.value_literals[name][value], 10) for value in blocked]


@pytest.mark.parametrize("mode_type", [SupremumReasoningMode, InfimumReasoningMode])
def test_reasoning_mode_absent_scalar_can_witness_its_first_value(mode_type: type[ReasoningStrategy]) -> None:
    mode = mode_type()
    name = clingo.String("value")
    mode.variable_lit = {name: 10}
    mode.scalar_variables = {name}
    mode.value_literals = {name: {None: 1, 3: 2}}
    mode.join({})

    assert mode.nogoods() == []

    mode.join({name: None})
    mode.join({})
    assert mode.rm_model == {name: {None}}
    assert mode.nogoods() == [(1, 10)]


@pytest.mark.parametrize("members", [frozenset(), frozenset({1}), frozenset({1, 2})])
def test_supremum_collection_nogoods_require_unseen_members(members: frozenset[int]) -> None:
    mode = SupremumReasoningMode()
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    mode.variable_lit = {items: 10, mapping: 11}
    mode.value_literals = {items: {1: 2, 2: 3}, mapping: {("key", 1): 4, ("key", 2): 5}}
    mode.join({items: members, mapping: multimap.Multimap.from_pairs(("key", value) for value in members)})

    assert mode.nogoods() == [
        (*(-literal for value, literal in mode.value_literals[items].items() if value not in members), 10),
        (*(-literal for (_, value), literal in mode.value_literals[mapping].items() if value not in members), 11),
    ]


@pytest.mark.parametrize(
    "left, right, expected",
    [
        ("same", "same", "same"),
        ("BOT", "BOT", "BOT"),
        ("left", "right", _LatticeBound.BOT),
        (3, "text", _LatticeBound.BOT),
        ("text", 3, _LatticeBound.BOT),
        (True, 1, _LatticeBound.BOT),
        ("BOT", 3, _LatticeBound.BOT),
        (3, "BOT", _LatticeBound.BOT),
        ("BOT", "text", _LatticeBound.BOT),
    ],
)
def test_infimum_joins_nonnumeric_values(left: object, right: object, expected: object) -> None:
    mode = InfimumReasoningMode()
    name = clingo.String("value")
    mode.join({name: left})
    mode.join({name: right})
    assert mode.rm_model == {name: {expected}}


@pytest.mark.parametrize(
    "current, candidates, blocked",
    [
        (2, [1, 2, 3], [2, 3]),
        (2.5, [1.5, 2.5, 3.5], [2.5, 3.5]),
        (False, [False, True], [False, True]),
        (True, [False, True], [True]),
        ("same", ["same", "other", 3], ["same"]),
        (_LatticeBound.BOT, ["same", "BOT", 3], ["same", "BOT", 3]),
        ("BOT", ["same", "BOT", 3], ["BOT"]),
        (3, [2, 3, "text"], [3]),
    ],
)
def test_infimum_scalar_nogoods_only_allow_improvement(
    current: object, candidates: list[object], blocked: list[object]
) -> None:
    mode = InfimumReasoningMode()
    name = clingo.String("value")
    mode.variable_lit = {name: 10}
    mode.scalar_variables = {name}
    mode.value_literals = {name: {value: literal for literal, value in enumerate(candidates, 1)}}
    mode.join({name: current})

    assert mode.nogoods() == [(mode.value_literals[name][value], 10) for value in blocked]


@pytest.mark.parametrize("members", [frozenset(), frozenset({1}), frozenset({1, 2})])
def test_infimum_collection_nogoods_require_removing_retained_members(members: frozenset[int]) -> None:
    mode = InfimumReasoningMode()
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    mode.variable_lit = {items: 10, mapping: 11}
    mode.value_literals = {items: {1: 2, 2: 3}, mapping: {("key", 1): 4, ("key", 2): 5}}
    mode.join({items: members, mapping: multimap.Multimap.from_pairs(("key", value) for value in members)})

    assert [frozenset(nogood) for nogood in mode.nogoods()] == [
        frozenset([*(literal for value, literal in mode.value_literals[items].items() if value in members), 10]),
        frozenset([*(literal for (_, value), literal in mode.value_literals[mapping].items() if value in members), 11]),
    ]


def test_collection_values_reuse_candidate_literals_without_presence_helpers() -> None:
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    scalar = clingo.String("scalar")
    variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable] = {
        scalar: _ScalarVariable(scalar, [_Value(1, 4), _Value(2, 5)]),
        items: _SetVariable(items, expression.Variable("items"), [_Value(1, 1), _Value(2, 2)]),
        mapping: _MultimapVariable(mapping, [_PairValue(3, "key", 1)]),
    }
    mode = UnionReasoningMode()
    mode.variable_lit = {scalar: 10, items: 11, mapping: 12}
    init = _InitRecorder()

    mode._init_literals(cast(clingo.PropagateInit, init), variables)

    assert init.frozen == [110, 111, 112]
    assert init.clauses == []
    assert mode.scalar_variables == {scalar}
    assert mode.value_literals == {
        scalar: {4: 1, 5: 2},
        items: {1: 1, 2: 2},
        mapping: {("key", 1): 3},
    }


@pytest.mark.xfail(reason="Python set equality currently conflates True and 1")
def test_set_variable_update_preserves_python_equal_members() -> None:
    class Model:
        def is_true(self, literal: int) -> bool:
            return literal in {1, 2}

    variable = _SetVariable(
        clingo.String("items"),
        expression.Variable("items"),
        [_Value(1, 1), _Value(2, True)],
    )

    variable.update(cast(clingo.Model, Model()))

    assert len(variable.value) == 2


@pytest.mark.xfail(reason="Python equality currently conflates bool and int candidates")
def test_scalar_and_multimap_values_preserve_bool_and_int_identity() -> None:
    class Model:
        def __init__(self, true_literals: set[int]) -> None:
            self.true_literals = true_literals

        def is_true(self, literal: int) -> bool:
            return literal in self.true_literals

    scalar = clingo.String("scalar")
    mapping = clingo.String("mapping")
    scalar_variable = _ScalarVariable(scalar, [_Value(1, 1), _Value(2, True)])
    mapping_variable = _MultimapVariable(
        mapping,
        [_PairValue(3, "key", 1), _PairValue(4, "key", True)],
    )
    mode = UnionReasoningMode()
    mode.variable_lit = {scalar: 10, mapping: 11}
    init = _InitRecorder()

    mode._init_literals(
        cast(clingo.PropagateInit, init),
        {scalar: scalar_variable, mapping: mapping_variable},
    )

    assert len(mode.value_literals[scalar]) == 2
    assert set(mode.value_literals[scalar].values()) == {1, 2}
    assert len(mode.value_literals[mapping]) == 2
    assert set(mode.value_literals[mapping].values()) == {3, 4}

    scalar_values = []
    for literal in (1, 2):
        scalar_variable.update(cast(clingo.Model, Model({literal})))
        scalar_values.append(scalar_variable.value)
        mode.join({scalar: scalar_variable.value})
    mapping_variable.update(cast(clingo.Model, Model({3, 4})))
    mode.join({mapping: mapping_variable.value})

    assert {(type(value), value) for value in scalar_values} == {(int, 1), (bool, True)}
    assert len(mode.rm_model[scalar]) == 2
    assert len(mapping_variable.value["key"]) == 2
    assert {(type(value), value) for value in mapping_variable.value["key"]} == {(int, 1), (bool, True)}
    assert len(mode.rm_model[mapping]) == 1


def test_reasoning_strategy_member_nogoods_handle_sets_and_multimaps() -> None:
    mode = UnionReasoningMode()
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    mode.value_literals = {
        items: {1: 2, 2: 3},
        mapping: {("key", 1): 4, ("key", 2): 5},
    }
    set_value = frozenset({1})
    map_value = multimap.Multimap.from_pairs([("key", 1)])

    assert mode._set_or_multimap_member_nogood(items, set_value, 10) == (2, 10)
    assert mode._set_or_multimap_member_nogood(mapping, map_value, 11) == (4, 11)
    assert mode._set_or_multimap_member_nogood(items, set_value, 10, union=True) == (-3, 10)
    assert mode._set_or_multimap_member_nogood(mapping, map_value, 11, union=True) == (-5, 11)


def test_reasoning_mode_propagator_builds_model_from_accepted_values() -> None:
    control = clingo.Control(["0"])
    mode = _RecordingReasoningStrategy()
    propagator = ReasoningModesPropagator(ReasoningMode.UNION)
    propagator.reasoning_strategy = mode
    control.register_propagator(propagator)
    control.add(
        "base",
        [],
        """
        1 { _se_value(variable("scalar"), val(int, 3));
            _se_value(variable("scalar"), val(int, 4)) } 1.
        _se_value(variable("items"), ref(set, variable("items"))).
        _set_contains(variable("items"), val(int, 7)).
        _set_contains(variable("items"), val(int, 8)).
        _se_value(variable("mapping"), ref(multimap, variable("mapping"))).
        multimap_value("mapping", val(string, "key"), val(int, 9)).
        """,
    )
    control.ground([("base", [])])
    propagator.prepare(control)
    control.solve()
    assert mode.models == []
    control.solve(on_model=propagator.on_model)

    scalar = clingo.String("scalar")
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    assert {model[scalar] for model in mode.models} == {3, 4}
    assert all(model[items] == frozenset({7, 8}) for model in mode.models)
    expected_mapping = multimap.Multimap.from_pairs([("key", 9)])
    assert all(model[mapping] == expected_mapping for model in mode.models)


def test_intersection_propagator_callback_pruning_reports_progress_models() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.INTERSECTION)
    control.register_propagator(propagator)
    control.add(
        "base",
        [],
        """
        1 { _se_value(variable("scalar"), val(int, 3));
            _se_value(variable("scalar"), val(int, 4)) } 1.
        { auxiliary(1..5) }.
        """,
    )
    control.ground([("base", [])])
    reported = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        reported.append(set(model.symbols(atoms=True)))

    propagator.prepare(control)
    solved = control.solve(on_model=on_model)
    assert solved.satisfiable
    assert len(reported) == 2
    assert propagator.reasoning_strategy.rm_model == {}

    reported.clear()
    propagator.prepare(control)
    assert control.solve(on_model=on_model).satisfiable
    assert len(reported) == 2


def test_intersection_propagator_whole_value_join_never_revives_values() -> None:
    mode = IntersectionReasoningMode()
    scalar = clingo.String("scalar")
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    mode.join({scalar: 1, items: frozenset({1, 2}), mapping: multimap.Multimap.from_pairs([("key", 1), ("key", 2)])})
    mode.join({scalar: 2, items: frozenset({2, 3}), mapping: multimap.Multimap.from_pairs([("key", 2), ("key", 3)])})
    mode.join({scalar: 1, items: frozenset({1, 2, 3}), mapping: multimap.Multimap.from_pairs([("key", 1), ("key", 2)])})
    assert mode.rm_model == {}


def test_intersection_propagator_drops_scalar_absent_from_a_model() -> None:
    mode = IntersectionReasoningMode()
    scalar = clingo.String("scalar")

    mode.join({scalar: 1})
    mode.join({})

    assert mode.rm_model == {}


def test_intersection_propagator_optional_scalar_has_empty_intersection() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.INTERSECTION)
    control.register_propagator(propagator)
    control.add("base", [], '{ _se_value(variable("scalar"), val(int, 1)) }.')
    control.ground([("base", [])])
    reported: list[dict[clingo.Symbol, set[object]]] = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        reported.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

    propagator.prepare(control)
    assert control.solve(on_model=on_model).satisfiable
    assert reported[-1] == {}


def test_intersection_propagator_instances_are_independent() -> None:
    first = ReasoningModesPropagator(ReasoningMode.INTERSECTION)
    second = ReasoningModesPropagator(ReasoningMode.INTERSECTION)
    assert first.reasoning_strategy is not second.reasoning_strategy


def test_intersection_propagator_empty_collection_is_a_complete_value() -> None:
    mode = IntersectionReasoningMode()
    items = clingo.String("items")
    mode.variable_lit = {items: 10}
    mode.value_literals = {items: {1: 2, 2: 3}}
    mode.join({items: frozenset()})
    mode.join({items: frozenset()})

    assert mode.rm_model == {items: {frozenset()}}
    assert {tuple(nogood) for nogood in mode.nogoods()} == {(-2, -3, 10), (-10,)}

    mode.join({items: frozenset({1})})
    mode.join({items: frozenset()})
    assert mode.rm_model == {}
    assert {tuple(nogood) for nogood in mode.nogoods()} == {(10,), ()}


def test_intersection_propagator_nogoods_require_one_retained_value_to_change() -> None:
    mode = IntersectionReasoningMode()
    scalar = clingo.String("scalar")
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    mode.variable_lit = {scalar: 10, items: 11, mapping: 12}
    mode.scalar_variables = {scalar}
    mode.value_literals = {
        scalar: {7: 2},
        items: {1: 4, 2: 5, 3: 7},
        mapping: {("key", 1): 6, ("key", 2): 8},
    }
    mode.join({scalar: 7, items: frozenset({1, 2}), mapping: multimap.Multimap.from_pairs([("key", 1)])})

    nogoods = {tuple(nogood) for nogood in mode.nogoods()}
    assert nogoods == {(2, 10), (4, 5, -7, 11), (6, -8, 12), (-10, -11, -12)}

    mode.join({scalar: 8, items: frozenset(), mapping: multimap.Multimap.from_pairs([])})
    assert {tuple(nogood) for nogood in mode.nogoods()} == {(10,), (11,), (12,), ()}


def test_intersection_propagator_prunes_nonshrinking_collection_models() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.INTERSECTION)
    control.register_propagator(propagator)
    control.add(
        "base",
        [],
        """
        _se_value(variable("items"), ref(set, variable("items"))).
        _set_contains(variable("items"), val(int, 1)).
        { _set_contains(variable("items"), val(int, 2)) }.
        _se_value(variable("mapping"), ref(multimap, variable("mapping"))).
        multimap_value("mapping", val(string, "key"), val(int, 1)).
        { multimap_value("mapping", val(string, "key"), val(int, 2)) }.
        { auxiliary(1..5) }.
        """,
    )
    control.ground([("base", [])])
    accumulated: list[dict[clingo.Symbol, set[object]]] = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        accumulated.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

    propagator.prepare(control)
    solved = control.solve(on_model=on_model)
    assert solved.satisfiable
    assert 2 <= len(accumulated) <= 3
    assert all(previous != current for previous, current in pairwise(accumulated))
    assert propagator.reasoning_strategy.rm_model == {}


def test_intersection_propagator_reasoning_modes_fixture_keeps_only_constant_c() -> None:
    control = clingo.Control(["0"])
    add_to_control(control, engine=engine.compile, reasoning_mode=ReasoningMode.INTERSECTION)
    control.load(str(Path(__file__).parent / "correctness" / "core" / "reasoning_modes.lp"))
    control.ground()
    reported: list[set[clingo.Symbol]] = []

    def on_model(model: clingo.Model) -> None:
        reported.append({atom for atom in model.symbols(theory=True) if atom.name == "model_intersection"})

    solved = control.solve(on_model=on_model)
    assert solved.satisfiable
    assert reported
    assert reported[-1] == {clingo.parse_term("model_intersection(c,val(bool,true))")}


def test_reasoning_mode_propagator_callback_joins_before_adding_all_nogoods() -> None:
    class CallbackStrategy(_RecordingReasoningStrategy):
        def nogoods(self) -> list[Iterable[int]]:
            assert self.models == [{}]
            return [(42,), (43,), ()]

    class Model:
        context = _NogoodContext()

    propagator = ReasoningModesPropagator(ReasoningMode.UNION)
    strategy = CallbackStrategy()
    propagator.reasoning_strategy = strategy
    model = Model()
    propagator.on_model(cast(clingo.Model, model))
    assert strategy.models == [{}]
    assert model.context.added == [(42,), (43,), ()]


def test_union_propagator_accumulates_whole_values() -> None:
    scalar = clingo.String("scalar")
    items = clingo.String("items")
    mapping = clingo.String("mapping")
    first = multimap.Multimap.from_pairs([("key", 1)])
    second = multimap.Multimap.from_pairs([("key", 2)])
    whole = UnionReasoningMode()
    whole.join({scalar: 1, items: frozenset(), mapping: first})
    whole.join({scalar: 2, items: frozenset({2}), mapping: second})
    whole.join({scalar: 1, items: frozenset(), mapping: first})
    assert whole.rm_model == {scalar: {1, 2}, items: {frozenset(), frozenset({2})}, mapping: {first, second}}


def test_union_propagator_nogoods_block_seen_complete_values() -> None:
    mode = UnionReasoningMode()
    scalar = clingo.String("scalar")
    items = clingo.String("items")
    mode.variable_lit = {scalar: 10, items: 11}
    mode.scalar_variables = {scalar}
    mode.value_literals = {scalar: {1: 2, 2: 4}, items: {1: 5, 2: 6}}
    mode.join({scalar: 1, items: frozenset()})
    mode.join({scalar: 1, items: frozenset({1})})
    nogoods = {frozenset(nogood) for nogood in mode.nogoods()}
    assert nogoods == {
        frozenset({2, 10}),
        frozenset({-5, -6, 11}),
        frozenset({5, -6, 11}),
    }


def test_union_propagator_callback_pruning_reports_strict_growth() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.UNION)
    control.register_propagator(propagator)
    control.add(
        "base",
        [],
        """
        1 { _se_value(variable("scalar"), val(int, 1));
            _se_value(variable("scalar"), val(int, 2)) } 1.
        _se_value(variable("items"), ref(set, variable("items"))).
        { _set_contains(variable("items"), val(int, 1)) }.
        _se_value(variable("mapping"), ref(multimap, variable("mapping"))).
        { multimap_value("mapping", val(string, "key"), val(int, 1)) }.
        { auxiliary(1..5) }.
        """,
    )
    control.ground([("base", [])])
    accumulated: list[dict[clingo.Symbol, set[object]]] = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        accumulated.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

    expected: dict[clingo.Symbol, set[object]] = {
        clingo.String("scalar"): {1, 2},
        clingo.String("items"): {frozenset({1})},
        clingo.String("mapping"): {multimap.Multimap.from_pairs([("key", 1)])},
    }
    expected[clingo.String("items")].add(frozenset())
    expected[clingo.String("mapping")].add(multimap.Multimap.from_pairs([]))
    for _ in range(2):
        accumulated.clear()
        propagator.prepare(control)
        assert control.solve(on_model=on_model).satisfiable
        assert 2 <= len(accumulated) <= 4
        assert all(previous != current for previous, current in pairwise(accumulated))
        assert propagator.reasoning_strategy.rm_model == expected


@pytest.mark.parametrize(
    "reasoning_mode, scalar_bound, members",
    [
        (ReasoningMode.SUPREMUM, 3, frozenset({0, 1, 2})),
        (ReasoningMode.INFIMUM, 1, frozenset({0})),
    ],
)
def test_extremum_propagator_callback_pruning_reports_strict_progress(
    reasoning_mode: ReasoningMode, scalar_bound: int, members: frozenset[int]
) -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(reasoning_mode)
    control.register_propagator(propagator)
    control.add(
        "base",
        [],
        """
        1 { _se_value(variable("scalar"), val(int, 1..3)) } 1.
        _se_value(variable("items"), ref(set, variable("items"))).
        _set_contains(variable("items"), val(int, 0)).
        1 { _set_contains(variable("items"), val(int, 1..2)) } 1.
        _se_value(variable("mapping"), ref(multimap, variable("mapping"))).
        multimap_value("mapping", val(string, "key"), val(int, 0)).
        1 { multimap_value("mapping", val(string, "key"), val(int, 1..2)) } 1.
        { auxiliary(1..5) }.
        """,
    )
    control.ground([("base", [])])
    accumulated: list[dict[clingo.Symbol, set[object]]] = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        accumulated.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

    expected: dict[clingo.Symbol, set[object]] = {
        clingo.String("scalar"): {scalar_bound},
        clingo.String("items"): {members},
        clingo.String("mapping"): {multimap.Multimap.from_pairs(("key", value) for value in members)},
    }
    combine = (
        SupremumReasoningMode._supremum if reasoning_mode == ReasoningMode.SUPREMUM else InfimumReasoningMode._infimum
    )
    for _ in range(2):
        accumulated.clear()
        propagator.prepare(control)
        assert control.solve(on_model=on_model).satisfiable
        assert 2 <= len(accumulated) <= 5
        for previous, current in pairwise(accumulated):
            assert previous != current
            for name in previous:
                assert combine(next(iter(previous[name])), next(iter(current[name]))) == next(iter(current[name]))
        assert propagator.reasoning_strategy.rm_model == expected


@pytest.mark.parametrize("reasoning_mode", [ReasoningMode.SUPREMUM, ReasoningMode.INFIMUM])
@pytest.mark.parametrize(
    "program, expected_supremum, expected_infimum, expected_satisfiable, max_models, expected_model_count",
    [
        ('_se_value(variable("value"), val(string, "same")).', {"same"}, {"same"}, True, 1, None),
        (
            (
                '1 { _se_value(variable("value"), val(string, "left")); '
                '_se_value(variable("value"), val(string, "right")) } 1.'
            ),
            {_LatticeBound.TOP},
            {_LatticeBound.BOT},
            True,
            2,
            None,
        ),
        (
            ('1 { _se_value(variable("value"), val(int, 3)); _se_value(variable("value"), val(string, "text")) } 1.'),
            {_LatticeBound.TOP},
            {_LatticeBound.BOT},
            True,
            2,
            None,
        ),
        (
            (
                '1 { _se_value(variable("value"), val(bool, false)); '
                '_se_value(variable("value"), val(bool, true)) } 1.'
            ),
            {True},
            {False},
            True,
            2,
            None,
        ),
        ('{ _se_value(variable("value"), val(int, 1..3)) } 1.', {3}, {1}, True, 4, None),
        (
            ('{ _se_value(variable("value"), val(int, 1)) }. :- _se_value(variable("value"), val(int, 1)).'),
            set(),
            set(),
            True,
            1,
            1,
        ),
        (
            '_se_value(variable("value"), ref(set, variable("value"))).',
            {frozenset()},
            {frozenset()},
            True,
            1,
            None,
        ),
        (
            '_se_value(variable("value"), ref(multimap, variable("value"))).',
            {multimap.Multimap.from_pairs([])},
            {multimap.Multimap.from_pairs([])},
            True,
            1,
            None,
        ),
        ("", set(), set(), True, 32, 32),
    ],
)
def test_extremum_propagator_scalar_and_empty_domains(
    reasoning_mode: ReasoningMode,
    program: str,
    expected_supremum: set[object],
    expected_infimum: set[object],
    expected_satisfiable: bool,
    max_models: int,
    expected_model_count: int | None,
) -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(reasoning_mode)
    control.register_propagator(propagator)
    control.add("base", [], program + " { auxiliary(1..5) }.")
    control.ground([("base", [])])
    accumulated: list[dict[clingo.Symbol, set[object]]] = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        accumulated.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

    expected = expected_supremum if reasoning_mode == ReasoningMode.SUPREMUM else expected_infimum
    for _ in range(2):
        accumulated.clear()
        propagator.prepare(control)
        assert control.solve(on_model=on_model).satisfiable is expected_satisfiable
        assert bool(accumulated) is expected_satisfiable
        assert len(accumulated) <= max_models
        if expected_model_count is not None:
            assert len(accumulated) == expected_model_count
        if expected:
            assert all(previous != current for previous, current in pairwise(accumulated))
        expected_model = {} if not expected else {clingo.String("value"): expected}
        if not expected:
            assert all(not model for model in accumulated)
        assert propagator.reasoning_strategy.rm_model == expected_model


def test_reasoning_mode_ignores_total_assignments_rejected_by_another_propagator() -> None:
    class RejectFirstValue(clingo.Propagator):
        def __init__(self) -> None:
            self.literal = 0
            self.rejected = 0

        def init(self, init: clingo.PropagateInit) -> None:
            atom = init.symbolic_atoms[clingo.parse_term('_se_value(variable("scalar"),val(int,1))')]
            assert atom is not None
            self.literal = init.solver_literal(atom.literal)
            init.check_mode = clingo.PropagatorCheckMode.Total

        def check(self, control: clingo.PropagateControl) -> None:
            if control.assignment.is_true(self.literal):
                self.rejected += 1
                control.add_nogood([self.literal])

    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.UNION)
    rejector = RejectFirstValue()
    control.register_propagator(propagator)
    control.register_propagator(rejector)
    control.add('1 { _se_value(variable("scalar"), val(int, 1..2)) } 1.')
    control.ground()
    propagator.prepare(control)

    assert control.solve(on_model=propagator.on_model).satisfiable
    assert rejector.rejected > 0
    assert propagator.reasoning_strategy.rm_model == {clingo.String("scalar"): {2}}


@pytest.mark.parametrize(
    "reasoning_mode, scalar_values, other_values",
    [
        (ReasoningMode.INTERSECTION, None, None),
        (ReasoningMode.UNION, {1, 2}, {4, 5}),
        (ReasoningMode.SUPREMUM, {2}, {5}),
        (ReasoningMode.INFIMUM, {1}, {4}),
    ],
)
def test_reasoning_mode_reuses_witnesses_after_cleanup_and_additional_grounding(
    reasoning_mode: ReasoningMode, scalar_values: set[int] | None, other_values: set[int] | None
) -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(reasoning_mode)
    control.register_propagator(propagator)
    control.add('1 { _se_value(variable("scalar"), val(int, 1..2)) } 1.')
    control.ground()
    scalar = clingo.String("scalar")
    other = clingo.String("other")
    propagator.prepare(control)
    witnesses = propagator._witnesses.copy()
    assert len(witnesses) == 1

    for _ in range(2):
        propagator.prepare(control)
        assert propagator._witnesses == witnesses
        assert control.solve(on_model=propagator.on_model).satisfiable
        expected = {} if scalar_values is None else {scalar: scalar_values}
        assert propagator.reasoning_strategy.rm_model == expected
        control.cleanup()

    control.add("extra", [], '1 { _se_value(variable("other"), val(int, 4..5)) } 1.')
    control.ground([("extra", [])])
    propagator.prepare(control)
    assert len(propagator._witnesses) == 2
    assert propagator._witnesses[scalar] == witnesses[scalar]
    assert control.solve(on_model=propagator.on_model).satisfiable
    expected = {} if scalar_values is None else {scalar: scalar_values, other: other_values}
    assert propagator.reasoning_strategy.rm_model == expected


@pytest.mark.xfail(reason="Standard mode currently leaves aggregate witness choices unconstrained")
def test_reasoning_mode_propagator_switches_modes_between_solves() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(ReasoningMode.UNION)
    control.register_propagator(propagator)
    control.add("base", [], '1 { _se_value(variable("scalar"), val(int, 1..2)) } 1.')
    control.ground([("base", [])])

    def solve_in_mode(mode: ReasoningMode) -> list[dict[clingo.Symbol, set[object]]]:
        propagator.set_mode(mode)
        reported: list[dict[clingo.Symbol, set[object]]] = []

        def on_model(model: clingo.Model) -> None:
            propagator.on_model(model)
            reported.append({name: values.copy() for name, values in propagator.reasoning_strategy.rm_model.items()})

        propagator.prepare(control)
        assert control.solve(on_model=on_model).satisfiable
        return reported

    scalar = clingo.String("scalar")
    union_models = solve_in_mode(ReasoningMode.UNION)
    assert len(union_models) == 2
    assert union_models[-1] == {scalar: {1, 2}}

    intersection_models = solve_in_mode(ReasoningMode.INTERSECTION)
    assert len(intersection_models) == 2
    assert intersection_models[-1] == {}

    standard_models = solve_in_mode(ReasoningMode.STANDARD)
    assert len(standard_models) == 2
    assert standard_models[-1] == {}

    union_models = solve_in_mode(ReasoningMode.UNION)
    assert len(union_models) == 2
    assert union_models[-1] == {scalar: {1, 2}}


@pytest.mark.parametrize("callback_style", ["keyword", "positional", "yield", "none", "limit"])
@pytest.mark.parametrize("early_stop", [False, True])
def test_reasoning_mode_wrapper_updates_output_before_user_callback(callback_style: str, early_stop: bool) -> None:
    control = clingo.Control(["1" if callback_style == "limit" else "0"])
    add_to_control(control, engine=engine.compile, reasoning_mode=ReasoningMode.UNION)
    control.add("variable_declare(a,fromFacts). variable_domain(a,val(int,1..2)).")
    control.ground()
    seen: set[int] = set()
    reported: list[set[int]] = []

    def on_model(model: clingo.Model) -> bool:
        current = {
            atom.arguments[1].arguments[1].number
            for atom in model.symbols(atoms=True, theory=True)
            if atom.name == "value" and str(atom.arguments[0]) == "a"
        }
        accumulated = {
            atom.arguments[1].arguments[1].number
            for atom in model.symbols(theory=True)
            if atom.name == "model_union" and str(atom.arguments[0]) == "a"
        }
        assert len(current) == 1
        seen.update(current)
        assert accumulated == seen
        reported.append(accumulated)
        return not early_stop

    for _ in range(2):
        seen.clear()
        reported.clear()
        if callback_style in {"keyword", "limit"}:
            solved = control.solve(on_model=on_model)
        elif callback_style == "positional":
            solved = control.solve([], on_model)
        elif callback_style == "yield":
            with control.solve(yield_=True) as handle:
                for model in handle:
                    if not on_model(model):
                        handle.cancel()
                        break
                solved = handle.get()
        else:
            solved = control.solve()
            assert control.statistics["summary"]["models"]["enumerated"] == 2
        assert solved.satisfiable
        if callback_style != "none":
            assert len(reported) == (1 if early_stop or callback_style == "limit" else 2)
            if not early_stop and callback_style != "limit":
                assert seen == {1, 2}


@pytest.mark.parametrize(
    "reasoning_mode, output_name, expected_value",
    [
        (ReasoningMode.SUPREMUM, "model_supremum", 2),
        (ReasoningMode.INFIMUM, "model_infimum", 1),
    ],
)
def test_reasoning_mode_wrapper_emits_extremum_atoms_before_user_callback(
    reasoning_mode: ReasoningMode, output_name: str, expected_value: int
) -> None:
    control = clingo.Control(["0"])
    add_to_control(control, engine=engine.compile, reasoning_mode=reasoning_mode)
    control.add("base", [], "variable_declare(a,fromFacts). variable_domain(a,val(int,1..2)).")
    control.ground()
    reported: list[set[clingo.Symbol]] = []

    def on_model(model: clingo.Model) -> None:
        reported.append({atom for atom in model.symbols(theory=True) if atom.name == output_name})

    assert control.solve(on_model=on_model).satisfiable
    assert reported
    assert reported[-1] == {clingo.parse_term(f"{output_name}(a,val(int,{expected_value}))")}


def test_standard_reasoning_mode_keeps_ordinary_enumeration() -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator()
    control.register_propagator(propagator)
    control.add("{ auxiliary(1..3) }.")
    control.ground()
    propagator.prepare(control)
    reported = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        reported.append(set(model.symbols(atoms=True)))

    assert control.solve(on_model=on_model).satisfiable
    assert len(reported) == 8
    assert propagator._witnesses == {}
    assert propagator.reasoning_strategy.rm_model == {}


@pytest.mark.parametrize(
    "reasoning_mode",
    [ReasoningMode.INTERSECTION, ReasoningMode.UNION, ReasoningMode.SUPREMUM, ReasoningMode.INFIMUM],
)
def test_aggregate_reasoning_modes_keep_models_without_tracked_variables(reasoning_mode: ReasoningMode) -> None:
    control = clingo.Control(["0"])
    propagator = ReasoningModesPropagator(reasoning_mode)
    control.register_propagator(propagator)
    control.add("base", [], "{ auxiliary(1..3) }.")
    control.ground([("base", [])])
    reported = []

    def on_model(model: clingo.Model) -> None:
        propagator.on_model(model)
        reported.append(set(model.symbols(atoms=True)))

    propagator.prepare(control)
    assert control.solve(on_model=on_model).satisfiable
    assert len(reported) == 8
    assert propagator.reasoning_strategy.rm_model == {}
