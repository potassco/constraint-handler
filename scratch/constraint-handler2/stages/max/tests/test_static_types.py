"""Tests for static type computation and diagnostics."""

from dataclasses import FrozenInstanceError
from unittest.mock import patch

import pytest

from constraint_handler import (
    ConstraintStore,
    Diagnostic,
    Diagnostics,
    DiagnosticSeverity,
    ExpressionLocation,
    Lambda,
    Operation,
    Operator,
    Python,
    VariableRef,
)
from constraint_handler.internal_input import Lambda as InternalLambda
from constraint_handler.internal_input import Operation as InternalOperation
from constraint_handler.internal_input import ValueDef, ValueType
from constraint_handler.python_input import Expr, OperationArg
from constraint_handler.type_checking import (
    UNKNOWN,
    SetOf,
    TupleType,
    Type,
    TypeCache,
    TypeChecker,
    UnknownType,
    union_types,
)
from constraint_handler.util import compute_evaluation_order


@pytest.mark.parametrize(
    ("operator", "expected"),
    (
        (Operator.length, frozenset({ValueType.integer})),
        (Operator.linear_integer, frozenset({ValueType.integer})),
        (Operator.linear_comparison, frozenset({ValueType.boolean})),
        (Operator.eq, frozenset({ValueType.boolean})),
        (Operator.sqrt, frozenset({ValueType.integer, ValueType.real})),
    ),
)
def test_cache_fixed_results_ignore_operands(
    operator: Operator, expected: Type
) -> None:
    """Infer declared results even for missing, invalid, or unresolved operands."""
    types = TypeCache(ConstraintStore())
    for args in ((), (ValueDef(ValueType.integer, 42),), (VariableRef("missing"),)):
        assert types.get_type(InternalOperation(operator, args)) == expected


def test_cache_bindings_are_snapshots() -> None:
    """Keep distinct bindings immutable and reject only conflicting writes."""
    parameter = VariableRef("parameter")
    body = InternalOperation(Operator.add, (parameter, ValueDef(ValueType.integer, 1)))
    types = TypeCache(ConstraintStore())
    integer = frozenset({ValueType.integer})
    real = frozenset({ValueType.real})
    bindings: dict[VariableRef, Type] = {parameter: integer}
    assert types.get_type(body, bindings) == integer
    bindings[parameter] = real
    assert types.get_type(body, bindings) == real
    assert types.get_type(body, {parameter: integer}) == integer
    types.set_type(body, real, bindings)
    with pytest.raises(ValueError):
        types.set_type(body, integer, bindings)


@pytest.mark.parametrize(
    "known", (UNKNOWN, frozenset[ValueType](), frozenset({ValueType.string}))
)
def test_cache_trusts_supplied_results(known: Type) -> None:
    """Treat unknown and empty entries as results and unify absent and empty bindings."""
    types = TypeCache(ConstraintStore())
    expression = InternalOperation(Operator.length, ())
    types.set_type(expression, known)
    assert types.get_type(expression, {}) is known
    types.set_type(expression, known, {})


def test_cache_structural_keys_and_cycles() -> None:
    """Do not reuse an ID's old expression type or recurse forever through sources."""
    store = ConstraintStore()
    variable = VariableRef("cycle")
    store.define(variable, variable)
    store.ensure(1)
    types = TypeCache(store)
    root = store.constraints[0].expr
    assert types.get_type(store.expressions[root]) == frozenset({ValueType.integer})
    store.replace_expression(root, ValueDef(ValueType.string, "new"))
    assert types.get_type(store.expressions[root]) == frozenset({ValueType.string})
    assert types.get_type(variable) is UNKNOWN


def test_cache_lambda_unknown_parameter_shadows_global() -> None:
    """Bind unknown arguments explicitly and still infer a fixed-result body."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.define(parameter, 1)
    body = InternalOperation(Operator.length, (parameter,))
    expression = InternalOperation(
        Operator.lambda_, (InternalLambda((parameter,), body), VariableRef("missing"))
    )
    types = TypeCache(store)
    assert types.get_type(expression) == frozenset({ValueType.integer})
    assert types.get_type(parameter, {parameter: UNKNOWN}) is UNKNOWN


def test_cache_lambda_does_not_rebind_global_sources() -> None:
    """Shadow direct references without changing another global's declaration."""
    store = ConstraintStore()
    parameter, alias = VariableRef("parameter"), VariableRef("alias")
    store.define(parameter, "text")
    store.define(alias, parameter)
    types = TypeCache(store)
    bindings = {parameter: frozenset({ValueType.integer})}
    assert types.get_type(parameter, bindings) == frozenset({ValueType.integer})
    assert types.get_type(alias, bindings) == frozenset({ValueType.string})


def test_checker_does_not_trust_cache_as_validation() -> None:
    """Check invalid operands even when the caller supplied a trusted result type."""
    store = ConstraintStore()
    store.define(VariableRef("result"), Operation(Operator.length, (42,)))
    expression = next(iter(store.expressions.values()))
    types = TypeCache(store)
    types.set_type(expression, frozenset({ValueType.integer}))
    checker = TypeChecker(types)
    diagnostics = checker.check(store)
    assert len(diagnostics) == 1
    assert "length" in next(iter(diagnostics)).message
    assert checker.check(store) == diagnostics


def test_checker_separates_runtime_shape_failures() -> None:
    """Leave tuple bounds and callback parameter-count failures to runtime."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.define(VariableRef("tuple"), Operation(Operator.tuple_get, ((1,), 4)))
    store.define(
        VariableRef("call"),
        Operation(Operator.lambda_, (Lambda((parameter,), parameter),)),
    )
    assert not TypeChecker(TypeCache(store)).check(store)


def test_checker_unknown_lambda_checks_known_siblings() -> None:
    """Unknown parameters shadow globals without suppressing independent errors."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.define(parameter, "text")
    callback = Lambda((parameter,), Operation(Operator.add, (parameter, "wrong")))
    store.define(
        VariableRef("result"),
        Operation(Operator.lambda_, (callback, VariableRef("missing"))),
    )
    diagnostics = TypeChecker(TypeCache(store)).check(store)
    assert len(diagnostics) == 1
    assert "add" in next(iter(diagnostics)).message


@pytest.mark.parametrize("known", (UNKNOWN, frozenset[ValueType]()))
def test_cache_memoizes_unknown_and_empty_computations(known: Type) -> None:
    """Never interpret unknown or empty completed results as cache misses."""
    types = TypeCache(ConstraintStore())
    expression = VariableRef("result")
    with patch(
        "constraint_handler.type_checking._type_inference._TypeInference.compute",
        return_value=known,
    ) as compute:
        assert types.get_type(expression) is known
        assert types.get_type(expression) is known
        compute.assert_called_once()


def test_cache_fixed_results_do_not_traverse_operands() -> None:
    """Avoid requesting operand types when the operator determines its result."""
    types = TypeCache(ConstraintStore())
    missing = VariableRef("missing")
    expression = InternalOperation(Operator.length, (missing,))
    assert types.get_type(expression) == frozenset({ValueType.integer})
    types.set_type(missing, frozenset({ValueType.string}))


def test_typing_never_executes_python_callbacks() -> None:
    """Treat source descriptors as opaque during both inference and checking."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(
        result, Operation(Operator.python_eval, (Python("raise_if_executed()"),))
    )
    types = TypeCache(store)
    with patch(
        "constraint_handler.python_conversion.compile_python",
        side_effect=AssertionError("Source must not be compiled"),
    ):
        assert types.get_type(result) is UNKNOWN
        assert not TypeChecker(types).check(store)


@pytest.mark.parametrize(
    "statement",
    (
        "constraint",
        "choice",
        "definition",
        "default",
        "set_base",
        "set_assignment",
        "set_default",
    ),
)
def test_checker_boolean_statement_contracts(statement: str) -> None:
    """Require Boolean constraint roots and all declaration conditions."""
    store = ConstraintStore()
    variable = VariableRef("variable")
    if statement == "constraint":
        store.ensure(1)
    elif statement == "choice":
        store.choose(variable, 1, condition=1)
    elif statement == "definition":
        store.define(variable, 1, condition=1)
    elif statement == "default":
        store.default_to(variable, 1, condition=1)
    elif statement == "set_base":
        store.set_contain_choose(variable, 1, condition=1)
    elif statement == "set_assignment":
        store.set_contain(variable, 1, condition=1)
    else:
        store.set_contain_default_to(variable, 1, condition=1)
    before = store.copy()
    diagnostics = TypeChecker(TypeCache(store)).check(store)
    assert len(diagnostics) == 1
    assert "must be boolean" in next(iter(diagnostics)).message
    assert store == before


def test_checker_keeps_binding_messages_at_shared_expression() -> None:
    """Keep each binding's message while sharing one located expression across roots."""
    store = ConstraintStore()
    parameter, argument = VariableRef("parameter"), VariableRef("argument")
    store.choose_from_iterator(argument, (1, 1.5))
    callback = Lambda((parameter,), Operation(Operator.concat, (1, "invalid")))
    for name, value in (("first", argument), ("second", 2)):
        store.define(VariableRef(name), Operation(Operator.lambda_, (callback, value)))
    diagnostics = TypeChecker(TypeCache(store)).check(store)
    locations = {item.location for item in diagnostics if item.location is not None}
    assert len(locations) == 1


@pytest.mark.parametrize(
    "values, warning", (((1, 1.5), False), ((1, "text"), True), ((True,), True))
)
def test_checker_equality_union_warnings(
    values: tuple[Expr, ...], warning: bool
) -> None:
    """Warn for any incompatible alternative without rejecting cross-type equality."""
    store = ConstraintStore()
    argument = VariableRef("argument")
    store.choose_from_iterator(argument, values)
    store.ensure(Operation(Operator.eq, (argument, 1)))
    diagnostics = TypeChecker(TypeCache(store)).check(store)
    assert len(diagnostics) == int(warning)
    assert all(item.severity == DiagnosticSeverity.warning for item in diagnostics)


@pytest.mark.parametrize(
    "operator", (Operator.set_make, Operator.union, Operator.inter, Operator.diff)
)
def test_checker_rejects_known_collection_shapes_with_unknown_members(
    operator: Operator,
) -> None:
    """Keep syntactically known collections out of scalar set-member positions."""
    store = ConstraintStore()
    unknown = Operation(Operator.python_eval, (Python("lambda: 1"),))
    collection = Operation(
        operator, (unknown, unknown) if operator == Operator.diff else (unknown,)
    )
    store.define(VariableRef("result"), Operation(Operator.set_make, (collection,)))
    diagnostics = TypeChecker(TypeCache(store)).check(store)
    assert len(diagnostics) == 1
    assert next(iter(diagnostics)).message == "set_make requires scalar arguments"


@pytest.mark.parametrize(
    ("expr", "condition", "valid"),
    (
        (5, True, True),
        (5, False, True),
        (1.5, True, False),
        (True, True, False),
        ("cost", True, False),
        (5, 1, False),
        (5, None, False),
    ),
)
def test_optimization_statement_types(expr: Expr, condition: Expr, valid: bool) -> None:
    """Require integer objectives and Boolean guards without conflating scalar types."""
    store = ConstraintStore()
    store.minimize(expr, condition)
    diagnostics = Diagnostics()
    diagnostics.items.extend(TypeChecker(TypeCache(store)).check(store))
    assert diagnostics.has_errors is not valid
    assert all(item.location is not None for item in diagnostics.items)


def test_expression_location_is_immutable() -> None:
    """Keep an analysis node in an immutable location value."""
    store = ConstraintStore()
    store.ensure(True)
    expression = store.expressions[store.constraints[0].expr]
    location = ExpressionLocation(expression)
    assert location.expression is expression
    for attribute in ("expression",):
        with pytest.raises(FrozenInstanceError):
            setattr(location, attribute, None)


@pytest.mark.parametrize(
    "arguments",
    (
        (),
        ("bad", 0),
        (VariableRef("input"), 0),
        (True, 0),
        ("eq",),
        ("eq", (0.5, 1), 0),
        ("eq", (True, 1), 0),
        ("eq", (1, 1.5), 0),
        ("eq", (1, True), 0),
        ("eq", (1, "text"), 0),
        ("eq", (VariableRef("input"), 1), 0),
        ("eq", (1, 1), 0.5),
        ("eq", (1, 1), VariableRef("input")),
        ("eq", 1, 0),
    ),
)
def test_linear_comparison_rejects_invalid_arguments(
    arguments: tuple[OperationArg, ...],
) -> None:
    """Reject malformed relations and all noninteger linear components."""
    store = ConstraintStore()
    store.define(VariableRef("input"), 1)
    store.ensure(Operation(Operator.linear_comparison, arguments))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert diagnostics.has_errors
    assert types.get_type(store.expressions[store.constraints[0].expr]) == frozenset(
        {ValueType.boolean}
    )


@pytest.mark.parametrize("severity", list(DiagnosticSeverity))
@pytest.mark.parametrize("located", [False, True])
@pytest.mark.parametrize("with_variable", [False, True])
def test_diagnostic_subjects(
    severity: DiagnosticSeverity, located: bool, with_variable: bool
) -> None:
    """Emit immutable diagnostics with independently optional expression and variable subjects."""
    store = ConstraintStore()
    store.ensure(True)
    root_id = store.constraints[0].expr
    location = (
        ExpressionLocation(store.expressions[root_id]) if located else None
    )
    variable = VariableRef("subject") if with_variable else None
    expected = Diagnostic(severity, "message", variable=variable, location=location)
    diagnostics = Diagnostics()
    emit = (
        diagnostics.warn
        if severity == DiagnosticSeverity.warning
        else diagnostics.error
    )
    emit("message", variable=variable, location=location)
    assert diagnostics.items == [expected]
    assert diagnostics.items[0].location is location
    for attribute in ("location", "variable", "message", "severity"):
        with pytest.raises(FrozenInstanceError):
            setattr(expected, attribute, None)


def test_nested_diagnostics_are_located_at_emission() -> None:
    """Attach each failing node before emission without replacing collected diagnostics."""
    store = ConstraintStore()
    store.ensure(True)
    store.ensure(
        (Operation(Operator.concat, (1, "x")), Operation(Operator.length, (1,)))
    )
    root_id = store.constraints[-1].expr
    root = store.expressions[root_id]
    assert isinstance(root, tuple)
    diagnostics = Diagnostics()
    diagnostics.warn("unlocated warning")
    warning = diagnostics.items[0]
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 2
    assert {item.location for item in diagnostics.errors} == {
        ExpressionLocation(expression) for expression in root
    }
    assert diagnostics.items[0] is warning
    assert warning.location is None


def test_nested_lambda_diagnostic_locates_expression() -> None:
    """Locate a failure inside nested lambda bodies by its analysis node."""
    store = ConstraintStore()
    store.ensure(True)
    outer, inner = VariableRef("outer"), VariableRef("inner")
    body = Operation(Operator.concat, (outer, inner))
    callback = Lambda(
        (outer,), Operation(Operator.lambda_, (Lambda((inner,), body), "x"))
    )
    store.ensure(Operation(Operator.lambda_, (callback, 1)))
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 1
    assert diagnostics.errors[0].location == ExpressionLocation(
        InternalOperation(Operator.concat, (outer, inner))
    )


def _static_types_for(store: ConstraintStore, diagnostics: Diagnostics) -> TypeCache:
    """Check standalone roots and declarations, leaving constraint contracts to statement tests."""
    compute_evaluation_order(store, diagnostics)
    context = store.copy()
    context.constraints.clear()
    types = TypeCache(context)
    diagnostics.items.extend(TypeChecker(types).check(context))
    return types


@pytest.mark.parametrize(
    "expression",
    [
        Operation(Operator.linear_integer, ((0.5, VariableRef("x")), 0)),
        Operation(Operator.linear_integer, ((1, VariableRef("x")), 0.5)),
        Operation(Operator.linear_integer, ((1, VariableRef("real")), 0)),
        Operation(Operator.linear_integer, ((VariableRef("x"), VariableRef("x")), 0)),
        Operation(Operator.linear_integer, ((1, VariableRef("x")), VariableRef("x"))),
    ],
)
def test_linear_rejects_noninteger_and_nonconstant_inputs(
    expression: Operation,
) -> None:
    """Require literal integer coefficients and offsets and integer-valued terms."""
    store = ConstraintStore()
    store.define(VariableRef("x"), 2)
    store.define(VariableRef("real"), 0.5)
    result = VariableRef("result")
    store.define(result, expression)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(result) == frozenset({ValueType.integer})
    assert diagnostics.has_errors


def test_literals_and_variables() -> None:
    """Verify scalar literal types and variable choices, definitions, and defaults."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    z = VariableRef("z")
    empty_var = VariableRef("empty")
    store.choose(x, 1)
    store.define(x, 2.5)
    store.default_to(x, "fallback")
    store.define(y, True)
    store.define(z, None)
    store.choose_from_iterator(empty_var, ())

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert not diag.has_errors
    assert not diag.warnings
    assert types.get_type(x) == frozenset(
        {ValueType.integer, ValueType.real, ValueType.string}
    )
    assert types.get_type(y) == frozenset({ValueType.boolean})
    assert types.get_type(z) == frozenset({ValueType.none})
    assert types.get_type(empty_var) == frozenset()


@pytest.mark.parametrize("scalar_source", ["choice", "definition", "default", "empty"])
@pytest.mark.parametrize("with_members", [False, True])
def test_variable_combines_scalar_and_set_declarations(
    scalar_source: str, with_members: bool
) -> None:
    """Union complete value alternatives with the set built from member declarations."""
    store = ConstraintStore()
    variable = VariableRef("mixed")
    if scalar_source == "choice":
        store.choose(variable, "scalar", condition=False)
    elif scalar_source == "definition":
        store.define(variable, "scalar", condition=False)
    elif scalar_source == "default":
        store.default_to(variable, "scalar", condition=False)
    else:
        store.choose_from_iterator(variable, ())
    if with_members:
        store.set_contain(variable, 1)
    else:
        store.set_contain_choose_from_iterator(variable, ())
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    expected: set[ValueType | SetOf] = {
        SetOf(
            frozenset({ValueType.integer}) if with_members else frozenset(),
            not with_members,
        )
    }
    if scalar_source != "empty":
        expected.add(ValueType.string)
    assert types.get_type(variable) == frozenset(expected)
    assert not diagnostics.has_errors


@pytest.mark.parametrize("unknown_source", ["scalar", "set"])
def test_unknown_mixed_declaration_absorbs_all_alternatives(
    unknown_source: str,
) -> None:
    """Keep a mixed variable unknown if either declaration kind is unknown."""
    store = ConstraintStore()
    variable = VariableRef("mixed")
    unknown = Operation(Operator.python_eval, (Python("lambda: 1"),))
    store.define(variable, unknown if unknown_source == "scalar" else "scalar")
    store.set_contain(variable, unknown if unknown_source == "set" else 1)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(variable) is UnknownType()
    assert not diagnostics.has_errors


def test_mixed_declarations_merge_complete_sets_and_retain_tuple_alternatives() -> None:
    """Merge set metadata without treating complete values as member declarations."""
    store = ConstraintStore()
    variable = VariableRef("mixed")
    store.choose(variable, "scalar")
    store.define(variable, (True,))
    store.default_to(variable, frozenset({"member"}))
    store.set_contain(variable, 1, condition=False)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(variable) == frozenset(
        {
            ValueType.string,
            TupleType((frozenset({ValueType.boolean}),)),
            SetOf(frozenset({ValueType.integer, ValueType.string}), True),
        }
    )
    assert not diagnostics.has_errors


@pytest.mark.parametrize("fold", [False, True])
@pytest.mark.parametrize("empty", [False, True])
def test_duplicate_lambda_parameters_are_rejected(fold: bool, empty: bool) -> None:
    """Reject repeated parameter names even when the callback would not be invoked."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    callback = Lambda((parameter, VariableRef("parameter")), parameter)
    if fold:
        expression = Operation(
            Operator.set_fold, (callback, frozenset() if empty else frozenset({1}), 0)
        )
    else:
        argument: Expr = (
            Operation(Operator.tuple_get, ((), VariableRef("index")))
            if empty
            else "scalar"
        )
        store.define(VariableRef("index"), 0)
        expression = Operation(Operator.lambda_, (callback, argument, 1))
    store.ensure(expression)
    root_id = store.constraints[0].expr
    root = store.expressions[root_id]
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(root) is UnknownType()
    assert len(diagnostics.errors) == 1
    assert "distinct" in diagnostics.errors[0].message
    assert diagnostics.errors[0].location == ExpressionLocation(root)


def test_nested_lambda_parameters_can_shadow_outer_names() -> None:
    """Check distinctness within each lambda while allowing lexical shadowing."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    inner = Operation(Operator.lambda_, (Lambda((parameter,), parameter), "inner"))
    outer = Lambda((parameter,), (parameter, inner, parameter))
    store.ensure(Operation(Operator.lambda_, (outer, 1)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(store.expressions[store.constraints[0].expr]) == frozenset(
        {
            TupleType(
                (
                    frozenset({ValueType.integer}),
                    frozenset({ValueType.string}),
                    frozenset({ValueType.integer}),
                )
            )
        }
    )
    assert not diagnostics.has_errors


def test_set_variables_and_set_literals() -> None:
    """Verify set variable types and set literal expressions."""
    store = ConstraintStore()
    s1 = VariableRef("s1")
    s2 = VariableRef("s2")
    s_empty = VariableRef("s_empty")
    store.set_contain_choose(s1, 1)
    store.set_contain_default_to(s1, "a")
    store.set_contain(s2, 10)
    store.set_contain_choose_from_iterator(s_empty, ())
    store.ensure(frozenset())
    store.ensure(frozenset({1, 2.0}))

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert not diag.has_errors
    assert types.get_type(s1) == frozenset(
        {SetOf(frozenset({ValueType.integer, ValueType.string}), True)}
    )
    assert types.get_type(s2) == frozenset(
        {SetOf(frozenset({ValueType.integer}), False)}
    )
    assert types.get_type(s_empty) == frozenset({SetOf(frozenset(), True)})
    assert types.get_type(store.expressions[store.constraints[0].expr]) == frozenset(
        {SetOf(frozenset(), True)}
    )
    assert types.get_type(store.expressions[store.constraints[1].expr]) == frozenset(
        {SetOf(frozenset({ValueType.integer, ValueType.real}), False)}
    )


@pytest.mark.parametrize("condition", [False, VariableRef("condition")])
def test_conditional_set_assignment_can_be_empty(condition: bool | VariableRef) -> None:
    """Do not infer nonemptiness from membership guarded by a condition."""
    store = ConstraintStore()
    store.choose_from_iterator(VariableRef("condition"), (True, False))
    variable = VariableRef("members")
    store.set_contain(variable, 1, condition=condition)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(variable) == frozenset(
        {SetOf(frozenset({ValueType.integer}), True)}
    )


def test_unconditional_membership_overrides_conditional_emptiness() -> None:
    """One unconditional assigned member suffices to guarantee nonemptiness."""
    store = ConstraintStore()
    variable = VariableRef("members")
    store.set_contain(variable, 1, condition=False)
    store.set_contain(variable, "always", condition=True)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(variable) == frozenset(
        {SetOf(frozenset({ValueType.integer, ValueType.string}), False)}
    )


@pytest.mark.parametrize("with_unknown", [False, True])
@pytest.mark.parametrize("unknown_first", [False, True])
@pytest.mark.parametrize("source", ["base", "assignment", "default"])
@pytest.mark.parametrize("element", [(1, 2), frozenset({1})])
def test_invalid_set_element_does_not_produce_partial_type(
    element: tuple[int, int] | frozenset[int],
    with_unknown: bool,
    unknown_first: bool,
    source: str,
) -> None:
    """Diagnose known invalid members even alongside unknown member sources."""
    store = ConstraintStore()
    variable = VariableRef("members")
    unknown = Operation(Operator.python_eval, (Python("lambda: 1"),))
    if with_unknown and unknown_first:
        store.set_contain(variable, unknown)
    store.set_contain(variable, 1)
    if source == "base":
        store.set_contain_choose(variable, element)
    elif source == "default":
        store.set_contain_default_to(variable, element)
    else:
        store.set_contain(variable, element)
    if with_unknown and not unknown_first:
        store.set_contain(variable, unknown)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert isinstance(types.get_type(variable), UnknownType)
    assert len(diagnostics.errors) == 1
    assert diagnostics.errors[0].variable == variable


@pytest.mark.parametrize("nested", [False, True])
@pytest.mark.parametrize("with_unknown", [False, True])
def test_tuple_sets_and_nesting_before_unknown_propagation(
    nested: bool, with_unknown: bool
) -> None:
    """Accept scalar/set slots but reject nesting even when a sibling is unknown."""
    store = ConstraintStore()
    member = VariableRef("member")
    store.choose_from_iterator(member, (1, frozenset({1})))
    sibling: Expr = (
        Operation(Operator.python_eval, (Python("lambda: 1"),)) if with_unknown else 0
    )
    invalid = (member, sibling)
    store.ensure((invalid,) if nested else invalid)
    root_id = store.constraints[0].expr
    root = store.expressions[root_id]
    assert isinstance(root, tuple)
    rejected = root[0] if nested else root
    assert isinstance(rejected, tuple)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    for item in rejected:
        types.get_type(item)
    if nested:
        assert types.get_type(root) is UnknownType()
        assert len(diagnostics.errors) == 1
        assert diagnostics.errors[0].message == "Nested tuples are not supported"
        assert diagnostics.errors[0].location == ExpressionLocation(root)
    else:
        assert not diagnostics.has_errors
        assert types.get_type(root) == frozenset(
            {TupleType((types.get_type(rejected[0]), types.get_type(rejected[1])))}
        )


@pytest.mark.parametrize(
    "value", ["", "abc", (), (1, "two"), frozenset[int](), frozenset({1, 2})]
)
def test_length_supports_strings_sets_and_tuples(
    value: str | tuple[int | str, ...] | frozenset[int],
) -> None:
    """Accept empty and nonempty values of every length-bearing type."""
    store = ConstraintStore()
    result = VariableRef("length")
    store.define(result, Operation(Operator.length, (value,)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(result) == frozenset({ValueType.integer})


@pytest.mark.parametrize(
    "operator", (Operator.set_make, Operator.set_isin, Operator.set_notin)
)
@pytest.mark.parametrize("explicit", (False, True))
def test_unknown_tuple_cannot_be_a_set_member(
    operator: Operator, explicit: bool
) -> None:
    """Reject known compound members even when a tuple position has unknown type."""
    store = ConstraintStore()
    unknown = Operation(Operator.python_eval, (Python("lambda: 1"),))
    member = Operation(Operator.make_tuple, (unknown,)) if explicit else (unknown,)
    arguments = (member,) if operator == Operator.set_make else (member, frozenset({1}))
    store.ensure(Operation(operator, arguments))
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 1
    assert "requires" in diagnostics.errors[0].message


@pytest.mark.parametrize("operator", (Operator.set_isin, Operator.set_notin))
def test_set_membership_accepts_none_query(operator: Operator) -> None:
    """Accept None as a query element because sets may contain None."""
    store = ConstraintStore()
    element = VariableRef("element")
    store.choose_from_iterator(element, (None, 1))
    store.define(
        VariableRef("result"), Operation(operator, (element, frozenset({None})))
    )
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(VariableRef("result")) == frozenset({ValueType.boolean})


def test_fold_checks_lambda_body_and_nested_error_location() -> None:
    """Retain the containing ID and precise failing node inside a fold lambda."""
    store = ConstraintStore()
    accumulator, element = VariableRef("accumulator"), VariableRef("element")
    invalid = Operation(Operator.concat, (1, "x"))
    callback = Lambda(
        (element, accumulator), Operation(Operator.add, (invalid, accumulator))
    )
    store.ensure(True)
    result = VariableRef("fold")
    store.define(result, Operation(Operator.set_fold, (callback, frozenset({1}), 0)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert isinstance(types.get_type(result), UnknownType)
    assert len(diagnostics.errors) == 2
    diagnostic = next(item for item in diagnostics.errors if "concat" in item.message)
    assert diagnostic.location is not None
    assert diagnostic.location.expression == InternalOperation(
        Operator.concat,
        (ValueDef(ValueType.integer, 1), ValueDef(ValueType.string, "x")),
    )


@pytest.mark.parametrize("arity", [0, 1, 3])
def test_fold_requires_binary_lambda(arity: int) -> None:
    """Leave fold callback parameter-count failures to runtime."""
    store = ConstraintStore()
    parameters = tuple(VariableRef(f"parameter_{index}") for index in range(arity))
    store.ensure(
        Operation(Operator.set_fold, (Lambda(parameters, 1), frozenset({1}), 0))
    )
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert not diagnostics.errors


def test_fold_checks_accumulator_feedback() -> None:
    """Check later iterations when the callback changes the accumulator's type."""
    store = ConstraintStore()
    accumulator, element = VariableRef("accumulator"), VariableRef("element")
    callback = Lambda(
        (element, accumulator), Operation(Operator.length, (accumulator,))
    )
    store.ensure(Operation(Operator.set_fold, (callback, frozenset({1, 2}), "initial")))
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 1
    assert "length requires" in diagnostics.errors[0].message


@pytest.mark.parametrize(
    ("members", "initial", "body"),
    [
        (frozenset[int](), 0, Operation(Operator.concat, (1, "unreachable"))),
        (frozenset({1}), (), (VariableRef("accumulator"),)),
        (
            frozenset({1}),
            0,
            Operation(Operator.real_from_int, (VariableRef("element"),)),
        ),
    ],
)
def test_fold_empty_sets_and_type_growth(
    members: frozenset[int], initial: Expr, body: Expr
) -> None:
    """Terminate on scalar convergence and expanding tuple shapes without checking unreachable bodies."""
    store = ConstraintStore()
    callback = Lambda((VariableRef("element"), VariableRef("accumulator")), body)
    result = VariableRef("fold")
    store.define(result, Operation(Operator.set_fold, (callback, members, initial)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    if not members:
        assert len(diagnostics.errors) == 1
        assert "concat" in diagnostics.errors[0].message
    elif isinstance(initial, tuple):
        assert len(diagnostics.errors) == 1
        assert diagnostics.errors[0].message == "Nested tuples are not supported"
    else:
        assert not diagnostics.has_errors
    assert types.get_type(result) is UnknownType()


@pytest.mark.parametrize(
    "callback",
    [
        Python("lambda acc, item: acc + item"),
        Lambda((VariableRef("acc"), VariableRef("item")), 1),
    ],
)
def test_fold_unknown_set_and_python_callback(callback: Python | Lambda) -> None:
    """Keep unknown sets and opaque Python callbacks conservative without false errors."""
    store = ConstraintStore()
    members = VariableRef("members")
    store.define(members, Operation(Operator.python_eval, (Python("{1}"),)))
    store.ensure(Operation(Operator.set_fold, (callback, members, 0)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert diagnostics.has_errors is isinstance(callback, Python)
    assert types.get_type(store.expressions[store.constraints[0].expr]) is UnknownType()


def test_fold_rejects_nonset_input() -> None:
    """Report a fold's invalid collection independently of its lambda body."""
    store = ConstraintStore()
    callback = Lambda((VariableRef("acc"), VariableRef("item")), 1)
    store.ensure(Operation(Operator.set_fold, (callback, 1, 0)))
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 1
    assert "requires a set" in diagnostics.errors[0].message


def test_lambda_scope_metadata_does_not_overwrite_global_or_other_bindings() -> None:
    """Retain separate types for one body evaluated under multiple lambda arguments."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.define(parameter, "global")
    argument = VariableRef("argument")
    store.choose_from_iterator(argument, (1, 2.5))
    callback = Lambda((parameter,), Operation(Operator.add, (parameter, 1)))
    result = VariableRef("result")
    store.define(result, Operation(Operator.lambda_, (callback, argument)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(parameter) == frozenset({ValueType.string})
    call = store.expressions[store.variables[result].definitions[0].value]
    assert isinstance(call, InternalOperation)
    internal_callback = call.args[0]
    assert isinstance(internal_callback, InternalLambda)
    for scalar in (ValueType.integer, ValueType.real):
        kind = frozenset({scalar})
        assert types.get_type(internal_callback.expr, {parameter: kind}) == kind


@pytest.mark.parametrize(
    "operator", [Operator.add, Operator.sub, Operator.mult, Operator.mod, Operator.pow]
)
def test_numeric_union_semantics_preserve_integer_and_real_alternatives(
    operator: Operator,
) -> None:
    """Evaluate numeric unions per member rather than collapsing them to real."""
    store = ConstraintStore()
    argument, result = VariableRef("argument"), VariableRef("result")
    store.choose_from_iterator(argument, (1, 1.5))
    store.define(result, Operation(operator, (argument, 2)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(result) == frozenset({ValueType.integer, ValueType.real})


def test_length_mixed_collection_union_and_invalid_member() -> None:
    """Accept all length-bearing alternatives and reject a union with any invalid member."""
    store = ConstraintStore()
    argument, result = VariableRef("argument"), VariableRef("result")
    store.choose_from_iterator(argument, ("a", (1, 2), frozenset({1})))
    store.define(result, Operation(Operator.length, (argument,)))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    assert types.get_type(result) == frozenset({ValueType.integer})
    store.choose(argument, 1)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(result) == frozenset({ValueType.integer})
    assert len(diagnostics.errors) == 1


def test_cycle_dependents_are_unknown_while_independent_expressions_are_typed() -> None:
    """Report cycles and blocked dependents without losing independent type information."""
    store = ConstraintStore()
    cycle, dependent, independent = (
        VariableRef("cycle"),
        VariableRef("dependent"),
        VariableRef("independent"),
    )
    store.define(cycle, Operation(Operator.add, (cycle, 1)))
    store.define(dependent, Operation(Operator.length, (cycle,)))
    store.define(independent, (1, "ok"))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 2
    for variable in (cycle,):
        assert types.get_type(variable) is UnknownType()
        expr_id = store.variables[variable].definitions[0].value
        assert types.get_type(store.expressions[expr_id]) is UnknownType()
        assert any(
            error.location == ExpressionLocation(store.expressions[expr_id])
            and "cycle" in error.message
            for error in diagnostics.errors
        )
    assert types.get_type(independent) == frozenset(
        {TupleType((frozenset({ValueType.integer}), frozenset({ValueType.string})))}
    )
    assert types.get_type(dependent) == frozenset({ValueType.integer})
    dependent_id = store.variables[dependent].definitions[0].value
    assert any(
        error.location
        == ExpressionLocation(store.expressions[dependent_id])
        for error in diagnostics.errors
    )


def test_unknown_input_does_not_hide_known_contract_error() -> None:
    """Check known operands even when another argument has unknown type."""
    store = ConstraintStore()
    unknown = VariableRef("unknown")
    store.define(unknown, Operation(Operator.python_eval, (Python("1"),)))
    store.ensure(Operation(Operator.concat, (unknown, 1)))
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == 1
    assert "concat" in diagnostics.errors[0].message


def test_set_literal_checks_every_element_despite_unknown_types() -> None:
    """Retain all element metadata and diagnose independent failures in a set."""
    store = ConstraintStore()
    unknown = VariableRef("unknown")
    store.define(unknown, Operation(Operator.python_eval, (Python("1"),)))
    store.ensure(frozenset({unknown, (1,), Operation(Operator.concat, (1, "bad"))}))
    root_id = store.constraints[0].expr
    root = store.expressions[root_id]
    assert isinstance(root, frozenset)
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(root) is UnknownType()
    for element in root:
        types.get_type(element)
    assert len(diagnostics.errors) == 2
    assert any("concat" in error.message for error in diagnostics.errors)
    assert any("Set literal elements" in error.message for error in diagnostics.errors)
    assert all(
        error.location is not None
        for error in diagnostics.errors
    )


@pytest.mark.parametrize("with_unknown", [False, True])
def test_set_literal_propagates_empty_element_types(with_unknown: bool) -> None:
    """Distinguish impossible set literals from empty sets, retaining unknown precedence."""
    store = ConstraintStore()
    empty = VariableRef("empty")
    store.choose_from_iterator(empty, ())
    unknown = VariableRef("unknown")
    store.define(unknown, Operation(Operator.python_eval, (Python("1"),)))
    store.ensure(frozenset({empty, unknown if with_unknown else 1}))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    root = store.expressions[store.constraints[0].expr]
    assert types.get_type(root) == (UnknownType() if with_unknown else frozenset())
    assert len(diagnostics.errors) == 1
    assert diagnostics.errors[0].variable == empty


@pytest.mark.parametrize("with_unknown", [False, True])
def test_linear_checks_known_terms_before_propagation(with_unknown: bool) -> None:
    """Report a noninteger term even when another term is unknown or impossible."""
    store = ConstraintStore()
    index, operand = VariableRef("index"), VariableRef("operand")
    store.define(index, 0)
    store.define(
        operand,
        Operation(Operator.python_eval, (Python("1"),))
        if with_unknown
        else Operation(Operator.tuple_get, ((), index)),
    )
    store.ensure(Operation(Operator.linear_integer, ((1, operand), (1, "bad"), 0)))
    root_id = store.constraints[0].expr
    root = store.expressions[root_id]
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert types.get_type(root) == frozenset({ValueType.integer})
    assert len(diagnostics.errors) == 1
    assert "linear_integer terms must be integer" in diagnostics.errors[0].message
    assert diagnostics.errors[0].location == ExpressionLocation(root)


@pytest.mark.parametrize("with_unknown", [False, True])
@pytest.mark.parametrize(
    ("operator", "arguments", "message"),
    [
        (Operator.eq, (VariableRef("operand"),), "invalid arity"),
        (Operator.neq, (VariableRef("operand"),), "invalid arity"),
        (Operator.length, (VariableRef("operand"), 0), "length"),
        (Operator.get_or_else, (VariableRef("operand"),), "invalid arity"),
        (Operator.if_, (1, VariableRef("operand")), "if_ requires"),
        (Operator.ite, (1, VariableRef("operand"), 0), "ite requires"),
        (Operator.has_value, (VariableRef("operand"), 0), "invalid arity"),
        (Operator.cardinality, (VariableRef("operand"), 0), "cardinality"),
        (Operator.set_make, (VariableRef("operand"), (1,)), "set_make requires"),
        (Operator.set_isin, ((1,), VariableRef("operand")), "requires"),
        (Operator.set_isin, (VariableRef("operand"), 1), "requires"),
        (Operator.set_notin, ((1,), VariableRef("operand")), "requires"),
        (Operator.set_notin, (VariableRef("operand"), 1), "requires"),
        (Operator.union, (VariableRef("operand"), 1), "union requires"),
        (Operator.inter, (1, VariableRef("operand")), "inter requires"),
        (Operator.diff, (VariableRef("operand"), 1), "diff requires"),
        (Operator.subset, (1, VariableRef("operand")), "subset requires"),
        (
            Operator.tuple_get,
            (VariableRef("operand"), "bad"),
            "index must be an integer",
        ),
        (
            Operator.tuple_get,
            (1, VariableRef("operand")),
            "first argument must be a tuple",
        ),
        (Operator.tuple_get, (VariableRef("operand"),), "invalid arity"),
    ],
)
def test_value_operations_check_contracts_before_propagation(
    operator: Operator,
    arguments: tuple[Expr, ...],
    message: str,
    with_unknown: bool,
) -> None:
    """Diagnose known operand and arity errors despite unknown or empty siblings."""
    store = ConstraintStore()
    index, operand = VariableRef("index"), VariableRef("operand")
    store.define(index, 0)
    store.define(
        operand,
        Operation(Operator.python_eval, (Python("1"),))
        if with_unknown
        else Operation(Operator.tuple_get, ((), index)),
    )
    store.ensure(Operation(operator, arguments))
    root_id = store.constraints[0].expr
    root = store.expressions[root_id]
    diagnostics = Diagnostics()
    _static_types_for(store, diagnostics)
    assert len(diagnostics.errors) == (2 if operator == Operator.cardinality else 1)
    assert all(message in diagnostic.message for diagnostic in diagnostics.errors)
    assert all(
        diagnostic.location == ExpressionLocation(root)
        for diagnostic in diagnostics.errors
    )


@pytest.mark.parametrize("with_unknown", [False, True])
def test_valid_value_operations_propagate_without_false_errors(
    with_unknown: bool,
) -> None:
    """Allow unknown or empty operands when no independently known contract is violated."""
    store = ConstraintStore()
    index, operand = VariableRef("index"), VariableRef("operand")
    store.define(index, 0)
    store.define(
        operand,
        Operation(Operator.python_eval, (Python("1"),))
        if with_unknown
        else Operation(Operator.tuple_get, ((), index)),
    )
    for operator, arguments in (
        (Operator.eq, (operand, 1)),
        (Operator.neq, (operand, 1)),
        (Operator.length, (operand,)),
        (Operator.get_or_else, (operand, 1)),
        (Operator.if_, (operand, 1)),
        (Operator.ite, (operand, 1, 2)),
        (Operator.has_value, (operand,)),
        (Operator.cardinality, (operand,)),
        (Operator.set_make, (operand,)),
        (Operator.set_isin, (1, operand)),
        (Operator.set_notin, (operand, frozenset({1}))),
        (Operator.union, (operand, frozenset({1}))),
        (Operator.inter, (frozenset({1}), operand)),
        (Operator.diff, (operand, frozenset({1}))),
        (Operator.subset, (frozenset({1}), operand)),
        (Operator.tuple_get, (operand, 0)),
        (Operator.tuple_get, ((1,), operand)),
    ):
        store.ensure(Operation(operator, arguments))
    diagnostics = Diagnostics()
    types = _static_types_for(store, diagnostics)
    assert not diagnostics.has_errors
    for constraint in store.constraints:
        expression = store.expressions[constraint.expr]
        assert isinstance(expression, InternalOperation)
        if expression.op in {
            Operator.eq,
            Operator.neq,
            Operator.has_value,
            Operator.set_isin,
            Operator.set_notin,
            Operator.subset,
        }:
            assert types.get_type(expression) == frozenset({ValueType.boolean})
        elif expression.op in {Operator.length, Operator.cardinality}:
            assert types.get_type(expression) == frozenset({ValueType.integer})
        elif expression.op == Operator.if_:
            assert types.get_type(expression) == frozenset(
                {ValueType.integer, ValueType.none}
            )
        elif expression.op == Operator.ite:
            assert types.get_type(expression) == frozenset({ValueType.integer})
        else:
            assert types.get_type(expression) == (
                UNKNOWN if with_unknown else frozenset()
            )


def test_unknown_marker_is_singleton() -> None:
    """Reuse one immutable unknown marker across construction and union."""
    assert UnknownType() is UnknownType()
    assert union_types((frozenset({ValueType.integer}), UnknownType())) is UnknownType()


def test_static_type_store_owns_independent_global_and_scoped_maps() -> None:
    """Keep public cache operations separate across global and local bindings."""
    variable = VariableRef("value")
    integer = frozenset({ValueType.integer})
    string = frozenset({ValueType.string})
    scope = frozenset({(variable, string)})
    types = TypeCache(ConstraintStore())
    types.set_type(variable, integer)
    types.set_type(variable, string, dict(scope))
    assert types.get_type(variable) == integer
    assert types.get_type(variable, dict(scope)) == string
    assert types.get_type(variable, {variable: integer}) == integer
    with pytest.raises(ValueError):
        types.set_type(variable, string)
    assert not hasattr(types, "scoped_expressions")
    assert not hasattr(types, "items")


def test_tuples_and_tuple_get() -> None:
    """Verify tuple types and tuple_get projection."""
    store = ConstraintStore()
    x = VariableRef("x")
    idx = VariableRef("idx")
    empty_v = VariableRef("empty_v")
    store.choose_from_iterator(x, (1, 2.0))
    store.choose_from_iterator(idx, (0, 1))
    store.choose_from_iterator(empty_v, ())

    t_expr = (x, "hi")
    store.define(VariableRef("tup_var"), t_expr)
    store.define(VariableRef("t0"), Operation(Operator.tuple_get, (t_expr, 0)))
    store.define(VariableRef("t1"), Operation(Operator.tuple_get, (t_expr, 1)))
    store.define(VariableRef("t_dyn"), Operation(Operator.tuple_get, (t_expr, idx)))
    store.define(VariableRef("t_empty"), (empty_v, 1))

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert len(diag.errors) == 1
    assert diag.errors[0].variable == empty_v
    assert types.get_type(VariableRef("tup_var")) == frozenset(
        {
            TupleType(
                (
                    frozenset({ValueType.integer, ValueType.real}),
                    frozenset({ValueType.string}),
                )
            )
        }
    )
    assert types.get_type(VariableRef("t0")) == frozenset(
        {ValueType.integer, ValueType.real}
    )
    assert types.get_type(VariableRef("t1")) == frozenset({ValueType.string})
    assert types.get_type(VariableRef("t_dyn")) == frozenset(
        {ValueType.integer, ValueType.real, ValueType.string}
    )
    assert types.get_type(VariableRef("t_empty")) == frozenset()


def test_operators_type_table() -> None:
    """Verify operator result types across arithmetic, boolean, string, and set ops."""
    store = ConstraintStore()
    i = VariableRef("i")
    f = VariableRef("f")
    n = VariableRef("n")
    b = VariableRef("b")
    s = VariableRef("s")
    opt = VariableRef("opt")
    store.define(i, 1)
    store.define(f, 1.5)
    store.choose_from_iterator(n, (1, 1.5))
    store.define(b, True)
    store.define(s, "abc")
    store.define(opt, Operation(Operator.if_, (b, i)))

    cases: list[tuple[str, Operation, object]] = [
        ("eq", Operation(Operator.eq, (i, s)), frozenset({ValueType.boolean})),
        ("neq", Operation(Operator.neq, (i, f)), frozenset({ValueType.boolean})),
        (
            "concat",
            Operation(Operator.concat, (s, "d")),
            frozenset({ValueType.string}),
        ),
        (
            "length",
            Operation(Operator.length, (s,)),
            frozenset({ValueType.integer}),
        ),
        (
            "max",
            Operation(Operator.max, (i, f)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "min",
            Operation(Operator.min, (i, f)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "get_or_else",
            Operation(Operator.get_or_else, (opt, s)),
            frozenset({ValueType.integer, ValueType.string}),
        ),
        (
            "has_value",
            Operation(Operator.has_value, (opt,)),
            frozenset({ValueType.boolean}),
        ),
        (
            "abs",
            Operation(Operator.abs, (n,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        ("minus", Operation(Operator.minus, (i,)), frozenset({ValueType.integer})),
        (
            "sqrt",
            Operation(Operator.sqrt, (i,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "cos",
            Operation(Operator.cos, (i,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "sin",
            Operation(Operator.sin, (f,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "tan",
            Operation(Operator.tan, (i,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "acos",
            Operation(Operator.acos, (i,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "asin",
            Operation(Operator.asin, (f,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "atan",
            Operation(Operator.atan, (i,)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        ("floor", Operation(Operator.floor, (f,)), frozenset({ValueType.integer})),
        ("ceil", Operation(Operator.ceil, (f,)), frozenset({ValueType.integer})),
        ("add_int", Operation(Operator.add, (i, 2)), frozenset({ValueType.integer})),
        (
            "add_real",
            Operation(Operator.add, (i, f)),
            frozenset({ValueType.real}),
        ),
        (
            "add_mix",
            Operation(Operator.add, (n, i)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        ("sub", Operation(Operator.sub, (i, 1)), frozenset({ValueType.integer})),
        ("mult", Operation(Operator.mult, (i, 3)), frozenset({ValueType.integer})),
        ("mod", Operation(Operator.mod, (i, 2)), frozenset({ValueType.integer})),
        (
            "int_div",
            Operation(Operator.int_div, (f, i)),
            frozenset({ValueType.integer}),
        ),
        (
            "real_div",
            Operation(Operator.real_div, (i, 2)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "pow_ii",
            Operation(Operator.pow, (i, 2)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "pow_if",
            Operation(Operator.pow, (i, f)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        ("leq", Operation(Operator.leq, (i, f)), frozenset({ValueType.boolean})),
        ("lt", Operation(Operator.lt, (i, f)), frozenset({ValueType.boolean})),
        ("geq", Operation(Operator.geq, (i, f)), frozenset({ValueType.boolean})),
        ("gt", Operation(Operator.gt, (i, f)), frozenset({ValueType.boolean})),
        (
            "f2i",
            Operation(Operator.real_from_int, (i,)),
            frozenset({ValueType.real}),
        ),
        (
            "i2f",
            Operation(Operator.int_from_real, (f,)),
            frozenset({ValueType.integer}),
        ),
        ("conj", Operation(Operator.conj, (b, True)), frozenset({ValueType.boolean})),
        ("disj", Operation(Operator.disj, (b, False)), frozenset({ValueType.boolean})),
        ("limp", Operation(Operator.limp, (b, True)), frozenset({ValueType.boolean})),
        ("lxor", Operation(Operator.lxor, (b, True)), frozenset({ValueType.boolean})),
        ("leqv", Operation(Operator.leqv, (b, False)), frozenset({ValueType.boolean})),
        (
            "ite",
            Operation(Operator.ite, (b, i, s)),
            frozenset({ValueType.integer, ValueType.string}),
        ),
        ("lnot", Operation(Operator.lnot, (b,)), frozenset({ValueType.boolean})),
        ("snot", Operation(Operator.snot, (None,)), frozenset({ValueType.boolean})),
        ("wnot", Operation(Operator.wnot, (b,)), frozenset({ValueType.boolean})),
        (
            "linear_int",
            Operation(Operator.linear_integer, ((2, i), (-1, 3), 5)),
            frozenset({ValueType.integer}),
        ),
    ]
    for name, expr, _ in cases:
        store.define(VariableRef(name), expr)

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert not diag.has_errors
    assert types.get_type(opt) == frozenset({ValueType.integer, ValueType.none})
    for name, _, expected in cases:
        assert types.get_type(VariableRef(name)) == expected, name


def test_set_operations_and_call_operations() -> None:
    """Verify set operations, lambda calls, set_fold, and python_eval."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.choose_from_iterator(x, (1, 1.5))

    s_empty = VariableRef("s_empty")
    s_int = VariableRef("s_int")
    s_str = VariableRef("s_str")
    store.define(s_empty, Operation(Operator.set_make, ()))
    store.define(s_int, Operation(Operator.set_make, (1, 2)))
    store.define(s_str, Operation(Operator.set_make, ("a",)))

    store.define(VariableRef("u1"), Operation(Operator.union, (s_empty, s_empty)))
    store.define(VariableRef("u2"), Operation(Operator.union, (s_empty, s_int)))
    store.define(VariableRef("inter"), Operation(Operator.inter, (s_int, s_str)))
    store.define(VariableRef("diff"), Operation(Operator.diff, (s_int, s_str)))
    store.define(VariableRef("subset"), Operation(Operator.subset, (s_int, s_str)))
    store.define(VariableRef("isin"), Operation(Operator.set_isin, (1, s_int)))
    store.define(VariableRef("notin"), Operation(Operator.set_notin, ("a", s_str)))
    store.define(VariableRef("card"), Operation(Operator.cardinality, (s_int,)))

    param = VariableRef("x")
    lam = Lambda((param,), Operation(Operator.add, (param, 1)))
    store.define(VariableRef("lam_res"), Operation(Operator.lambda_, (lam, x)))
    store.define(
        VariableRef("py_res"),
        Operation(Operator.python_eval, (Python("x + 1"), x)),
    )
    fold_lam = Lambda(
        (VariableRef("acc"), VariableRef("el")),
        Operation(Operator.add, (VariableRef("acc"), VariableRef("el"))),
    )
    store.define(
        VariableRef("fold_res"),
        Operation(Operator.set_fold, (fold_lam, s_int, 0)),
    )
    store.define(
        VariableRef("absorb"),
        Operation(Operator.add, (VariableRef("py_res"), 1)),
    )

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert not diag.has_errors
    assert types.get_type(VariableRef("u1")) == frozenset({SetOf(frozenset(), True)})
    assert types.get_type(VariableRef("u2")) == frozenset(
        {SetOf(frozenset({ValueType.integer}), False)}
    )
    assert types.get_type(VariableRef("inter")) == frozenset(
        {SetOf(frozenset({ValueType.integer, ValueType.string}), True)}
    )
    assert types.get_type(VariableRef("diff")) == frozenset(
        {SetOf(frozenset({ValueType.integer}), True)}
    )
    assert types.get_type(VariableRef("subset")) == frozenset({ValueType.boolean})
    assert types.get_type(VariableRef("isin")) == frozenset({ValueType.boolean})
    assert types.get_type(VariableRef("notin")) == frozenset({ValueType.boolean})
    assert types.get_type(VariableRef("card")) == frozenset({ValueType.integer})
    assert types.get_type(VariableRef("lam_res")) == frozenset(
        {ValueType.integer, ValueType.real}
    )
    assert types.get_type(VariableRef("py_res")) == UnknownType()
    assert types.get_type(VariableRef("fold_res")) == UnknownType()
    assert types.get_type(VariableRef("absorb")) == UnknownType()


def test_lambda_empty_and_unknown_args() -> None:
    """Verify lambda call with empty and UnknownType arguments."""
    store = ConstraintStore()
    empty_v = VariableRef("empty_v")
    unk_v = VariableRef("unk_v")
    store.choose_from_iterator(empty_v, ())
    store.define(unk_v, Operation(Operator.python_eval, (Python("1"),)))

    p = VariableRef("p")
    lam = Lambda((p,), Operation(Operator.add, (p, 1)))
    store.define(VariableRef("res_empty"), Operation(Operator.lambda_, (lam, empty_v)))
    store.define(VariableRef("res_unk"), Operation(Operator.lambda_, (lam, unk_v)))
    store.define(VariableRef("op_empty"), Operation(Operator.add, (empty_v, 1)))
    store.define(
        VariableRef("lin_empty"),
        Operation(Operator.linear_integer, ((2, empty_v), 1)),
    )
    store.define(
        VariableRef("lin_unk"),
        Operation(Operator.linear_integer, ((2, unk_v), 1)),
    )
    store.define(VariableRef("set_unk"), frozenset({unk_v}))
    store.define(VariableRef("tup_unk"), (unk_v, 1))
    s_unk = VariableRef("s_unk")
    store.set_contain(s_unk, unk_v)

    types = _static_types_for(store, Diagnostics())
    assert types.get_type(VariableRef("res_empty")) == frozenset()
    assert types.get_type(VariableRef("res_unk")) == UnknownType()
    assert types.get_type(VariableRef("op_empty")) == frozenset()
    assert types.get_type(VariableRef("lin_empty")) == frozenset({ValueType.integer})
    assert types.get_type(VariableRef("lin_unk")) == frozenset({ValueType.integer})
    assert types.get_type(VariableRef("set_unk")) == UnknownType()
    assert types.get_type(VariableRef("tup_unk")) == frozenset(
        {TupleType((UNKNOWN, frozenset({ValueType.integer})))}
    )
    assert types.get_type(s_unk) == UnknownType()


def test_diagnostics_for_undefined_cycles_and_contract_violations() -> None:
    """Verify errors are collected in Diagnostics without aborting computation."""
    store = ConstraintStore()
    a = VariableRef("a")
    b = VariableRef("b")
    undef = VariableRef("undef")
    ok = VariableRef("ok")

    store.define(a, b)
    store.define(b, a)
    store.define(VariableRef("uses_undef"), Operation(Operator.add, (undef, 1)))
    store.define(ok, Operation(Operator.add, (1, 2)))

    # Contract violations
    store.ensure(Operation(Operator.concat, (1, "a")))
    store.ensure(Operation(Operator.length, (1,)))
    store.ensure(Operation(Operator.max, ("a",)))
    store.ensure(Operation(Operator.if_, (1, "a")))
    store.ensure(Operation(Operator.abs, ("a",)))
    store.ensure(Operation(Operator.sqrt, ("a",)))
    store.ensure(Operation(Operator.floor, ("a",)))
    store.ensure(Operation(Operator.add, ("a",)))
    store.ensure(Operation(Operator.sub, (1,)))
    store.ensure(Operation(Operator.int_div, (1,)))
    store.ensure(Operation(Operator.real_div, (1,)))
    store.ensure(Operation(Operator.pow, (1, "a")))
    store.ensure(Operation(Operator.leq, (1, "a")))
    store.ensure(Operation(Operator.real_from_int, (1.5,)))
    store.ensure(Operation(Operator.int_from_real, (1,)))
    store.ensure(Operation(Operator.conj, (1,)))
    store.ensure(Operation(Operator.limp, (True,)))
    store.ensure(Operation(Operator.ite, (1, 2, 3)))
    store.ensure(Operation(Operator.lnot, (1,)))
    store.ensure(Operation(Operator.snot, (1,)))
    store.ensure(Operation(Operator.cardinality, (1,)))
    store.ensure(Operation(Operator.set_make, ((1, 2),)))
    store.ensure(Operation(Operator.set_isin, (1, 2)))
    store.ensure(Operation(Operator.union, (1, 2)))
    store.ensure(Operation(Operator.inter, (1, 2)))
    store.ensure(Operation(Operator.diff, (1, 2)))
    store.ensure(Operation(Operator.subset, (1, 2)))
    store.ensure(Operation(Operator.eq, (1,)))
    store.ensure(Operation(Operator.get_or_else, (1,)))
    store.ensure(Operation(Operator.has_value, (1, 2)))
    store.ensure(Operation(Operator.python_eval, (1,)))
    store.ensure(Operation(Operator.set_fold, (1, 2)))
    store.ensure(Operation(Operator.set_fold, (1, frozenset({1}), 0)))
    store.ensure(Operation(Operator.lambda_, (1,)))
    store.ensure(Operation(Operator.lambda_, (Lambda((VariableRef("p"),), 1), 1, 2)))
    store.ensure(Operation(Operator.tuple_get, (1,)))
    store.ensure(Operation(Operator.tuple_get, ((1, 2), "bad")))
    store.ensure(Operation(Operator.tuple_get, (1, 0)))
    store.ensure(Operation(Operator.tuple_get, ((1, 2), 5)))
    store.ensure(Operation(Operator.linear_integer, ()))
    store.ensure(Operation(Operator.linear_integer, (1, 2)))
    store.ensure(Operation(Operator.linear_integer, (("bad", 1), 0)))
    store.ensure(Operation(Operator.add, (Python("1"),)))
    store.ensure(frozenset({(1, 2)}))
    bad_set = VariableRef("bad_set")
    store.set_contain(bad_set, (1, 2))

    diag = Diagnostics()
    types = _static_types_for(store, diag)
    assert diag.has_errors
    assert len(diag.errors) >= 35
    assert all(d.severity == DiagnosticSeverity.error for d in diag.errors)
    assert types.get_type(ok) == frozenset({ValueType.integer})
    assert types.get_type(a) == UnknownType()
    assert types.get_type(b) == UnknownType()


@pytest.mark.parametrize(
    ("t1", "t2", "expected"),
    [
        (
            frozenset({SetOf(frozenset({ValueType.integer}), False)}),
            frozenset({SetOf(frozenset({ValueType.string}), True)}),
            frozenset({SetOf(frozenset({ValueType.integer, ValueType.string}), True)}),
        ),
        (
            UnknownType(),
            frozenset({ValueType.integer}),
            UnknownType(),
        ),
    ],
)
def test_union_types_helper(t1: Type, t2: Type, expected: Type) -> None:
    """Verify union_types merges SetOf members and absorbs UnknownType."""
    assert union_types((t1, t2)) == expected
