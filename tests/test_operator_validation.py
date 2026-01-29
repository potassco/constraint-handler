"""
Test cases for operator argument validation.
"""


def test_set_diff_arg_validation():
    """Test that set diff operator only accepts exactly 2 arguments."""
    from constraint_handler.set import Evaluator, Operator

    evaluator = Evaluator()

    # Test with 0 arguments
    result = evaluator.operator(Operator.diff, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "diff takes exactly 2 arguments (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument
    evaluator.errors = []
    result = evaluator.operator(Operator.diff, [frozenset({1, 2, 3})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "diff takes exactly 2 arguments (1 were given)" in str(evaluator.errors[0])

    # Test with 2 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.diff, [frozenset({1, 2, 3}), frozenset({2, 3, 4})])
    assert result == frozenset({1})
    assert len(evaluator.errors) == 0

    # Test with 3 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.diff, [frozenset({1, 2, 3}), frozenset({2, 3, 4}), frozenset({1, 4, 5})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "diff takes exactly 2 arguments (3 were given)" in str(evaluator.errors[0])
