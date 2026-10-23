"""Tests for static type computation and diagnostics."""

import pytest

from constraint_handler import (
    ConstraintStore,
    Diagnostics,
    DiagnosticSeverity,
    Lambda,
    Operation,
    Operator,
    Python,
    VariableRef,
)
from constraint_handler.internal_input import ValueType
from constraint_handler.static_types import (
    SetOf,
    StaticTypeStore,
    TupleType,
    UnknownType,
    compute_static_types,
    union_types,
)
from constraint_handler.util import compute_evaluation_order


def _static_types_for(store: ConstraintStore, diagnostics: Diagnostics | None = None) -> StaticTypeStore:
    """Compute evaluation order and static types for a store."""
    diag = diagnostics if diagnostics is not None else Diagnostics()
    order = compute_evaluation_order(store, diag)
    return compute_static_types(store, order, diag)


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
    assert isinstance(types[result], UnknownType)
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
    assert types[x] == frozenset({ValueType.integer, ValueType.real, ValueType.string})
    assert types[y] == frozenset({ValueType.boolean})
    assert types[z] == frozenset({ValueType.none})
    assert types[empty_var] == frozenset()


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
    assert types[s1] == frozenset({SetOf(frozenset({ValueType.integer, ValueType.string}), True)})
    assert types[s2] == frozenset({SetOf(frozenset({ValueType.integer}), False)})
    assert types[s_empty] == frozenset({SetOf(frozenset(), True)})
    assert types[store.expressions[store.constraints[0].expr]] == frozenset({SetOf(frozenset(), True)})
    assert types[store.expressions[store.constraints[1].expr]] == frozenset(
        {SetOf(frozenset({ValueType.integer, ValueType.real}), False)}
    )


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
    assert types[VariableRef("tup_var")] == frozenset(
        {
            TupleType(
                (
                    frozenset({ValueType.integer, ValueType.real}),
                    frozenset({ValueType.string}),
                )
            )
        }
    )
    assert types[VariableRef("t0")] == frozenset({ValueType.integer, ValueType.real})
    assert types[VariableRef("t1")] == frozenset({ValueType.string})
    assert types[VariableRef("t_dyn")] == frozenset({ValueType.integer, ValueType.real, ValueType.string})
    assert types[VariableRef("t_empty")] == frozenset()


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
            Operation(Operator.min, (b, i)),
            frozenset({ValueType.boolean, ValueType.integer}),
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
        ("sqrt", Operation(Operator.sqrt, (i,)), frozenset({ValueType.real})),
        ("cos", Operation(Operator.cos, (i,)), frozenset({ValueType.real})),
        ("sin", Operation(Operator.sin, (f,)), frozenset({ValueType.real})),
        ("tan", Operation(Operator.tan, (i,)), frozenset({ValueType.real})),
        ("acos", Operation(Operator.acos, (i,)), frozenset({ValueType.real})),
        ("asin", Operation(Operator.asin, (f,)), frozenset({ValueType.real})),
        ("atan", Operation(Operator.atan, (i,)), frozenset({ValueType.real})),
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
            frozenset({ValueType.real}),
        ),
        (
            "pow_ii",
            Operation(Operator.pow, (i, 2)),
            frozenset({ValueType.integer, ValueType.real}),
        ),
        (
            "pow_if",
            Operation(Operator.pow, (i, f)),
            frozenset({ValueType.real}),
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
    assert types[opt] == frozenset({ValueType.integer, ValueType.none})
    for name, _, expected in cases:
        assert types[VariableRef(name)] == expected, name


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
    assert types[VariableRef("u1")] == frozenset({SetOf(frozenset(), True)})
    assert types[VariableRef("u2")] == frozenset({SetOf(frozenset({ValueType.integer}), False)})
    assert types[VariableRef("inter")] == frozenset({SetOf(frozenset({ValueType.integer, ValueType.string}), True)})
    assert types[VariableRef("diff")] == frozenset({SetOf(frozenset({ValueType.integer}), True)})
    assert types[VariableRef("subset")] == frozenset({ValueType.boolean})
    assert types[VariableRef("isin")] == frozenset({ValueType.boolean})
    assert types[VariableRef("notin")] == frozenset({ValueType.boolean})
    assert types[VariableRef("card")] == frozenset({ValueType.integer})
    assert types[VariableRef("lam_res")] == frozenset({ValueType.integer, ValueType.real})
    assert types[VariableRef("py_res")] == UnknownType()
    assert types[VariableRef("fold_res")] == UnknownType()
    assert types[VariableRef("absorb")] == UnknownType()


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

    types = _static_types_for(store)
    assert types[VariableRef("res_empty")] == frozenset()
    assert types[VariableRef("res_unk")] == UnknownType()
    assert types[VariableRef("op_empty")] == frozenset()
    assert types[VariableRef("lin_empty")] == frozenset()
    assert types[VariableRef("lin_unk")] == UnknownType()
    assert types[VariableRef("set_unk")] == UnknownType()
    assert types[VariableRef("tup_unk")] == UnknownType()
    assert types[s_unk] == UnknownType()


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
    assert types[ok] == frozenset({ValueType.integer})
    assert types[a] == UnknownType()
    assert types[b] == UnknownType()


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
def test_union_types_helper(t1: object, t2: object, expected: object) -> None:
    """Verify union_types merges SetOf members and absorbs UnknownType."""
    assert union_types((t1, t2)) == expected  # type: ignore[arg-type]
