"""Declarative input conversion and storage contracts."""

# pyright: reportPrivateUsage=false

from collections.abc import Iterable
from dataclasses import FrozenInstanceError

import pytest

from constraint_handler import (
    LABEL_ANONYMOUS,
    ConstraintStore,
    Lambda,
    Operation,
    Operator,
    Python,
    VariableRef,
    internal_input,
    python_input,
)
from constraint_handler.internal_input import ValueDef, ValueType


@pytest.mark.parametrize(
    ("value", "value_type"),
    [
        (True, ValueType.boolean),
        (False, ValueType.boolean),
        (1, ValueType.integer),
        (1.0, ValueType.real),
        ("hello", ValueType.string),
        (None, ValueType.none),
    ],
)
def test_scalar_types(value: python_input.Value, value_type: ValueType) -> None:
    """Verify that scalar conversion retains each literal's explicit type."""
    store = ConstraintStore()
    store.ensure(value)
    assert store._expressions[store.constraints[0].expr] == ValueDef(value_type, value)


def test_documented_usage() -> None:
    """Verify declarations, definitions, and constraints in the documented API."""
    store = ConstraintStore()
    name = VariableRef("x")
    store.choose_from_iterator(name, (1, 2), label="input")
    store.define(
        VariableRef("y"), Operation(Operator.add, (name, 1)), label="definition"
    )
    store.ensure(Operation(Operator.eq, (name, 2)), "required")
    store.check(Operation(Operator.gt, (name, 9)), "diagnostic")

    variable = store.variables[name]
    assert [element.label for element in variable.choices] == ["input", "input"]
    assert tuple(store._expressions[item.value] for item in variable.choices) == (
        ValueDef(ValueType.integer, 1),
        ValueDef(ValueType.integer, 2),
    )
    (defined,) = store.variables[VariableRef("y")].definitions
    assert defined.label == "definition"
    assert store._expressions[defined.value] == internal_input.Operation(
        Operator.add, (name, ValueDef(ValueType.integer, 1))
    )
    assert [(item.is_check, item.label) for item in store.constraints] == [
        (False, "required"),
        (True, "diagnostic"),
    ]
    assert store._expressions[store.constraints[0].expr] == internal_input.Operation(
        Operator.eq, (name, ValueDef(ValueType.integer, 2))
    )
    assert store._expressions[store.constraints[1].expr] == internal_input.Operation(
        Operator.gt, (name, ValueDef(ValueType.integer, 9))
    )


def test_choices_and_definitions_retain_conditions() -> None:
    """Verify choices and definitions store their condition as an expression ID."""
    store = ConstraintStore()
    name = VariableRef("x")
    guard = Operation(Operator.eq, (VariableRef("y"), 1))
    store.choose_from_iterator(name, (1, 2), guard, label="input")
    store.define(name, 3, guard, label="definition")
    store.define(name, 4)

    first, second = store.variables[name].choices
    assert first.condition == second.condition
    assert store._expressions[first.condition] == internal_input.Operation(
        Operator.eq, (VariableRef("y"), ValueDef(ValueType.integer, 1))
    )
    defined, unconditional = store.variables[name].definitions
    assert store._expressions[defined.condition] == internal_input.Operation(
        Operator.eq, (VariableRef("y"), ValueDef(ValueType.integer, 1))
    )
    assert store._expressions[unconditional.condition] == ValueDef(
        ValueType.boolean, True
    )


@pytest.mark.parametrize(
    "choices",
    [(1, 2), [1, 2], range(1, 3), iter((1, 2)), (value for value in (1, 2))],
    ids=["tuple", "list", "range", "iterator", "generator"],
)
def test_iterable_choices(choices: Iterable[python_input.Expr]) -> None:
    """Verify iterable choices are consumed into stored expression IDs."""
    store = ConstraintStore()
    name = VariableRef("x")
    store.choose_from_iterator(name, choices)
    stored_choices = store.variables[name].choices
    assert isinstance(stored_choices, list)
    assert all(element.label == LABEL_ANONYMOUS for element in stored_choices)
    assert tuple(store._expressions[item.value] for item in stored_choices) == (
        ValueDef(ValueType.integer, 1),
        ValueDef(ValueType.integer, 2),
    )


@pytest.mark.parametrize("choices", [(), [], iter(())])
def test_empty_choices(choices: Iterable[python_input.Expr]) -> None:
    """Verify that omitted and explicitly empty choices both store an empty list."""
    store = ConstraintStore()
    name = VariableRef("x")
    store.choose_from_iterator(name, choices)
    assert store.variables[name].choices == []


def test_omitted_choices_default_to_empty() -> None:
    """Verify that calling without choices stores an empty list."""
    store = ConstraintStore()
    name = VariableRef("x")
    store.choose_from_iterator(name)
    assert store.variables[name].choices == []


def test_repeated_choices_definitions_and_defaults() -> None:
    """Verify repeated inputs retain all entries and their individual labels."""
    store = ConstraintStore()
    name = VariableRef("x")
    store.define(name, 2)
    store.choose_from_iterator(name, (value for value in (1, 2)), label="candidates")
    store.default_to(name, 0)
    condition = Operation(Operator.eq, (name, 1))
    store.default_to(name, 3, condition, 1, "defaults")
    store.define(name, 3, label="definition")
    store.choose_from_iterator(name, (), label="empty")
    store.choose_from_iterator(name, (2, 3), label="more")

    variable = store.variables[name]
    assert [entry.label for entry in variable.choices] == [
        "candidates",
        "candidates",
        "more",
        "more",
    ]
    assert tuple(store._expressions[item.value] for item in variable.choices) == (
        ValueDef(ValueType.integer, 1),
        ValueDef(ValueType.integer, 2),
        ValueDef(ValueType.integer, 2),
        ValueDef(ValueType.integer, 3),
    )
    assert [entry.label for entry in variable.definitions] == [
        LABEL_ANONYMOUS,
        "definition",
    ]
    assert [store._expressions[entry.value] for entry in variable.definitions] == [
        ValueDef(ValueType.integer, 2),
        ValueDef(ValueType.integer, 3),
    ]
    first, second = variable.defaults
    assert store._expressions[first.value] == ValueDef(ValueType.integer, 0)
    assert store._expressions[first.condition] == ValueDef(ValueType.boolean, True)
    assert (first.priority, first.label) == (0, LABEL_ANONYMOUS)
    assert store._expressions[second.value] == ValueDef(ValueType.integer, 3)
    assert store._expressions[second.condition] == internal_input.Operation(
        Operator.eq, (name, ValueDef(ValueType.integer, 1))
    )
    assert (second.priority, second.label) == (1, "defaults")


def test_recursive_collections_and_calls_are_not_evaluated() -> None:
    """Verify recursive conversion without executing stored calls or bodies."""
    store = ConstraintStore()
    name = VariableRef("x")
    python = Python("1 / 0")
    body = Operation(Operator.add, (name, 1))
    expr = Operation(
        Operator.lambda_,
        (Lambda((name,), body), (True, 1, 1.0), frozenset({"a", name}), python),
    )
    store.ensure(expr)

    assert store._expressions[store.constraints[0].expr] == internal_input.Operation(
        Operator.lambda_,
        (
            internal_input.Lambda(
                (name,),
                internal_input.Operation(
                    Operator.add, (name, ValueDef(ValueType.integer, 1))
                ),
            ),
            (
                ValueDef(ValueType.boolean, True),
                ValueDef(ValueType.integer, 1),
                ValueDef(ValueType.real, 1.0),
            ),
            frozenset({ValueDef(ValueType.string, "a"), name}),
            python,
        ),
    )
    assert ValueDef(ValueType.boolean, True) != ValueDef(ValueType.integer, 1)
    assert ValueDef(ValueType.integer, 1) != ValueDef(ValueType.real, 1.0)
    assert not store.variables


def test_expression_types_are_public_and_immutable() -> None:
    """Verify public exports and immutable, hashable expression objects."""
    assert Operation is python_input.Operation
    assert Operator is internal_input.Operator
    assert ConstraintStore is internal_input.ConstraintStore
    name = VariableRef("x")
    assert {Operation(Operator.add, (name, 1))}
    with pytest.raises(FrozenInstanceError):
        name.__setattr__("name", "y")


def test_store_containers_are_independent() -> None:
    """Verify that variables and stores do not share mutable containers."""
    first = ConstraintStore()
    second = ConstraintStore()
    first.default_to(VariableRef("x"), 1)
    first.default_to(VariableRef("y"), 2)
    first.choose_from_iterator(VariableRef("x"), (1,))
    first.define(VariableRef("x"), 1)
    first.check(True)
    assert len(first.variables[VariableRef("x")].defaults) == 1
    assert len(first.variables[VariableRef("y")].defaults) == 1
    assert first.variables[VariableRef("y")].choices == []
    assert not first.variables[VariableRef("y")].definitions
    assert not second.variables
    assert not second.set_variables
    assert not second.constraints
    assert not second._expressions


def test_set_variable_bases_and_assigns() -> None:
    """Verify set variable candidate bases and mandatory assignments."""
    store = ConstraintStore()
    name = VariableRef("s")
    guard = Operation(Operator.eq, (VariableRef("x"), 1))
    store.set_contain_choose_from_iterator(name, (1, 2), guard, label="base")
    store.set_contain_choose_from_iterator(name)
    store.set_contain(name, 3, guard, label="assigned")
    store.set_contain(name, 4)

    set_var = store.set_variables[name]
    first_base, second_base = set_var.bases
    assert (first_base.label, second_base.label) == ("base", "base")
    assert first_base.condition == second_base.condition
    assert tuple(store._expressions[item.value] for item in set_var.bases) == (
        ValueDef(ValueType.integer, 1),
        ValueDef(ValueType.integer, 2),
    )
    first_assign, second_assign = set_var.assigns
    assert (first_assign.label, second_assign.label) == ("assigned", LABEL_ANONYMOUS)
    assert store._expressions[first_assign.value] == ValueDef(ValueType.integer, 3)
    assert store._expressions[first_assign.condition] == internal_input.Operation(
        Operator.eq, (VariableRef("x"), ValueDef(ValueType.integer, 1))
    )
    assert store._expressions[second_assign.value] == ValueDef(ValueType.integer, 4)
    assert store._expressions[second_assign.condition] == ValueDef(
        ValueType.boolean, True
    )
