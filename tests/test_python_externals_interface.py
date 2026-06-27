from __future__ import annotations

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.python_externals.interface as interface
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.warning as warning


def _clear_interface_caches() -> None:
    interface.pythonExpressionVariable.cache_clear()
    interface.pythonEnumerateVariables.cache_clear()
    interface.pythonEvalExpr.cache_clear()
    interface.pythonStatementVariables.cache_clear()


def test_python_expression_variable_returns_sorted_symbols():
    _clear_interface_caches()

    expr = (expression.Variable("b"), expression.Variable("a"))
    cl_expr = myClorm.pytocl(expr)

    result = interface.pythonExpressionVariable(cl_expr)

    assert result == [clingo.String("a"), clingo.String("b")]


def test_python_enumerate_variables_sorts_enumerated_symbols():
    _clear_interface_caches()

    expr = (expression.Variable("b"), expression.Variable("a"))
    cl_expr = myClorm.pytocl(expr)

    result = interface.pythonEnumerateVariables(cl_expr)

    expected_a_then_b = [
        myClorm.pytocl((0, "a")),
        myClorm.pytocl((1, "b")),
        clingo.Function("length", [clingo.Number(2)]),
    ]
    assert result == expected_a_then_b


def test_python_statement_variables_returns_sorted_symbols():
    _clear_interface_caches()

    cl_code = myClorm.pytocl("b = 1.0\na = 1")
    cl_in_types = myClorm.pytocl([])
    cl_id = myClorm.pytocl([])

    result = interface.pythonStatementVariables(cl_code, cl_in_types, cl_id)

    expected = sorted(
        [
            myClorm.pytocl(("a", interface.type_.BaseType.int)),
            myClorm.pytocl(("b", interface.type_.BaseType.float)),
        ]
    )
    assert result == expected
