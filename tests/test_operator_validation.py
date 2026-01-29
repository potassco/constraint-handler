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


def test_set_isin_arg_validation():
    """Test that set isin operator only accepts exactly 2 arguments."""
    from constraint_handler.set import Evaluator, Operator

    evaluator = Evaluator()

    # Test with 0 arguments
    result = evaluator.operator(Operator.isin, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "isin takes exactly 2 arguments (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument
    evaluator.errors = []
    result = evaluator.operator(Operator.isin, [1])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "isin takes exactly 2 arguments (1 were given)" in str(evaluator.errors[0])

    # Test with 2 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.isin, [1, frozenset({1, 2, 3})])
    assert result is True
    assert len(evaluator.errors) == 0

    # Test with 3 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.isin, [1, frozenset({1, 2, 3}), frozenset({1, 4, 5})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "isin takes exactly 2 arguments (3 were given)" in str(evaluator.errors[0])


def test_set_notin_arg_validation():
    """Test that set notin operator only accepts exactly 2 arguments."""
    from constraint_handler.set import Evaluator, Operator

    evaluator = Evaluator()

    # Test with 0 arguments
    result = evaluator.operator(Operator.notin, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "notin takes exactly 2 arguments (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument
    evaluator.errors = []
    result = evaluator.operator(Operator.notin, [1])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "notin takes exactly 2 arguments (1 were given)" in str(evaluator.errors[0])

    # Test with 2 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.notin, [5, frozenset({1, 2, 3})])
    assert result is True
    assert len(evaluator.errors) == 0

    # Test with 3 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.notin, [5, frozenset({1, 2, 3}), frozenset({1, 4, 5})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "notin takes exactly 2 arguments (3 were given)" in str(evaluator.errors[0])


def test_set_inter_arg_validation():
    """Test that set inter operator requires at least 1 argument."""
    from constraint_handler.set import Evaluator, Operator

    evaluator = Evaluator()

    # Test with 0 arguments
    result = evaluator.operator(Operator.inter, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "inter takes at least 1 argument (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.inter, [frozenset({1, 2, 3})])
    assert result == frozenset({1, 2, 3})
    assert len(evaluator.errors) == 0

    # Test with 2 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.inter, [frozenset({1, 2, 3}), frozenset({2, 3, 4})])
    assert result == frozenset({2, 3})
    assert len(evaluator.errors) == 0

    # Test with 3 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.inter, [frozenset({1, 2, 3}), frozenset({2, 3, 4}), frozenset({2, 4, 5})])
    assert result == frozenset({2})
    assert len(evaluator.errors) == 0


def test_set_subset_arg_validation():
    """Test that set subset operator only accepts exactly 2 arguments."""
    from constraint_handler.set import Evaluator, Operator

    evaluator = Evaluator()

    # Test with 0 arguments
    result = evaluator.operator(Operator.subset, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "subset takes exactly 2 arguments (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument
    evaluator.errors = []
    result = evaluator.operator(Operator.subset, [frozenset({1, 2})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "subset takes exactly 2 arguments (1 were given)" in str(evaluator.errors[0])

    # Test with 2 arguments (correct case)
    evaluator.errors = []
    result = evaluator.operator(Operator.subset, [frozenset({1, 2}), frozenset({1, 2, 3})])
    assert result is True
    assert len(evaluator.errors) == 0

    # Test with 3 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.subset, [frozenset({1, 2}), frozenset({1, 2, 3}), frozenset({1, 4, 5})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "subset takes exactly 2 arguments (3 were given)" in str(evaluator.errors[0])


def test_set_fold_arg_validation():
    """Test that set set_fold operator only accepts exactly 3 arguments."""
    from constraint_handler.set import Evaluator, Operator
    from constraint_handler.utils.common import PPEnum

    evaluator = Evaluator()
    TestOp = PPEnum("TestOp", ["add"])

    # Test with 0 arguments
    result = evaluator.operator(Operator.set_fold, [])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "set_fold takes exactly 3 arguments (0 were given)" in str(evaluator.errors[0])

    # Test with 1 argument
    evaluator.errors = []
    result = evaluator.operator(Operator.set_fold, [TestOp.add])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "set_fold takes exactly 3 arguments (1 were given)" in str(evaluator.errors[0])

    # Test with 2 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.set_fold, [TestOp.add, frozenset({1, 2, 3})])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "set_fold takes exactly 3 arguments (2 were given)" in str(evaluator.errors[0])

    # Test with 4 arguments
    evaluator.errors = []
    result = evaluator.operator(Operator.set_fold, [TestOp.add, frozenset({1, 2, 3}), 0, "extra"])
    assert result is None
    assert len(evaluator.errors) == 1
    assert isinstance(evaluator.errors[0], TypeError)
    assert "set_fold takes exactly 3 arguments (4 were given)" in str(evaluator.errors[0])
