"""
Test cases for operator argument validation.
"""

import constraint_handler.arithmetic as arithmetic
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning
import constraint_handler.set as myset
from constraint_handler.utils.common import Bad


def _assert_arity_error(errors, expected_text):
    assert len(errors) == 1
    kind, message = errors[0]
    assert kind == warning.Expression(warning.ExpressionWarning.syntaxError)
    assert expected_text in message


def test_set_diff_arg_validation():
    """Test that set diff operator only accepts exactly 2 arguments."""
    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.diff, [])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "diff takes exactly 2 arguments (0 were given)")

    # Test with 1 argument
    evaluated = myset.evaluate_operator(operators.SetOperator.diff, [frozenset({1, 2, 3})])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "diff takes exactly 2 arguments (1 was given)")

    # Test with 2 arguments (correct case)
    evaluated = myset.evaluate_operator(operators.SetOperator.diff, [frozenset({1, 2, 3}), frozenset({2, 3, 4})])
    result = evaluated.value
    assert result == frozenset({1})
    assert len(evaluated.errors) == 0

    # Test with 3 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.diff,
        [frozenset({1, 2, 3}), frozenset({2, 3, 4}), frozenset({1, 4, 5})],
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "diff takes exactly 2 arguments (3 were given)")


def test_set_isin_arg_validation():
    """Test that set isin operator only accepts exactly 2 arguments."""
    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.set_isin, [])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_isin takes exactly 2 arguments (0 were given)")

    # Test with 1 argument
    evaluated = myset.evaluate_operator(operators.SetOperator.set_isin, [1])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_isin takes exactly 2 arguments (1 was given)")

    # Test with 2 arguments (correct case)
    evaluated = myset.evaluate_operator(operators.SetOperator.set_isin, [1, frozenset({1, 2, 3})])
    result = evaluated.value
    assert result is True
    assert len(evaluated.errors) == 0

    # Test with 3 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_isin,
        [1, frozenset({1, 2, 3}), frozenset({1, 4, 5})],
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_isin takes exactly 2 arguments (3 were given)")


def test_set_notin_arg_validation():
    """Test that set notin operator only accepts exactly 2 arguments."""
    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.set_notin, [])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_notin takes exactly 2 arguments (0 were given)")

    # Test with 1 argument
    evaluated = myset.evaluate_operator(operators.SetOperator.set_notin, [1])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_notin takes exactly 2 arguments (1 was given)")

    # Test with 2 arguments (correct case)
    evaluated = myset.evaluate_operator(operators.SetOperator.set_notin, [5, frozenset({1, 2, 3})])
    result = evaluated.value
    assert result is True
    assert len(evaluated.errors) == 0

    # Test with 3 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_notin,
        [5, frozenset({1, 2, 3}), frozenset({1, 4, 5})],
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_notin takes exactly 2 arguments (3 were given)")


def test_set_inter_arg_validation():
    """Test that set inter operator requires at least 1 argument."""
    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.inter, [])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "inter takes at least 1 arguments (0 were given)")

    # Test with 1 argument (correct case)
    evaluated = myset.evaluate_operator(operators.SetOperator.inter, [frozenset({1, 2, 3})])
    result = evaluated.value
    assert result == frozenset({1, 2, 3})
    assert len(evaluated.errors) == 0

    # Test with 2 arguments (correct case)
    evaluated = myset.evaluate_operator(operators.SetOperator.inter, [frozenset({1, 2, 3}), frozenset({2, 3, 4})])
    result = evaluated.value
    assert result == frozenset({2, 3})
    assert len(evaluated.errors) == 0

    # Test with 3 arguments (correct case)
    evaluated = myset.evaluate_operator(
        operators.SetOperator.inter,
        [frozenset({1, 2, 3}), frozenset({2, 3, 4}), frozenset({2, 4, 5})],
    )
    result = evaluated.value
    assert result == frozenset({2})
    assert len(evaluated.errors) == 0


def test_set_subset_arg_validation():
    """Test that set subset operator only accepts exactly 2 arguments."""
    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.subset, [])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "subset takes exactly 2 arguments (0 were given)")

    # Test with 1 argument
    evaluated = myset.evaluate_operator(operators.SetOperator.subset, [frozenset({1, 2})])
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "subset takes exactly 2 arguments (1 was given)")

    # Test with 2 arguments (correct case)
    evaluated = myset.evaluate_operator(
        operators.SetOperator.subset,
        [frozenset({1, 2}), frozenset({1, 2, 3})],
    )
    result = evaluated.value
    assert result is True
    assert len(evaluated.errors) == 0

    # Test with 3 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.subset,
        [frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({1, 4, 5})],
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "subset takes exactly 2 arguments (3 were given)")


def test_set_fold_arg_validation():
    """Test that set_fold operator only accepts exactly 3 arguments."""

    def apply_operator(op, inner_args):
        return arithmetic.evaluate_operator(op, inner_args)

    # Test with 0 arguments
    evaluated = myset.evaluate_operator(operators.SetOperator.set_fold, [], apply_operator=apply_operator)
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_fold takes exactly 3 arguments (0 were given)")

    # Test with 1 argument
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_fold,
        [operators.ArithmeticOperator.add],
        apply_operator=apply_operator,
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_fold takes exactly 3 arguments (1 was given)")

    # Test with 2 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_fold,
        [operators.ArithmeticOperator.add, frozenset({1, 2, 3})],
        apply_operator=apply_operator,
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_fold takes exactly 3 arguments (2 were given)")

    # Test with 3 arguments (correct case)
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_fold,
        [operators.ArithmeticOperator.add, frozenset({1, 2, 3}), 0],
        apply_operator=apply_operator,
    )
    result = evaluated.value
    assert result == 6
    assert len(evaluated.errors) == 0

    # Test with 4 arguments
    evaluated = myset.evaluate_operator(
        operators.SetOperator.set_fold,
        [operators.ArithmeticOperator.add, frozenset({1, 2, 3}), 0, "extra"],
        apply_operator=apply_operator,
    )
    result = evaluated.value
    assert result == Bad.bad
    _assert_arity_error(evaluated.errors, "set_fold takes exactly 3 arguments (4 were given)")
