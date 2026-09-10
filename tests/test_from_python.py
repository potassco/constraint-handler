import clingo

import constraint_handler
import constraint_handler.myClorm as myClorm
from constraint_handler.schemas.atom import (
    Ensure,
    Optimize_maximizeSum,
    Optimize_modelValue,
    Optimize_value,
    Value,
    Variable_declare,
    Variable_define,
    Variable_domain,
)
from constraint_handler.schemas.domain import FromFacts
from constraint_handler.schemas.expression import Operation, Val, Variable
from constraint_handler.schemas.operators import ArithmeticOperator, ComparisonOperator
from constraint_handler.schemas.type_ import BaseType


def test_det():
    x = [Variable_define("x", Val(BaseType.int, 5))]
    y = [Variable_define("y", Variable("x"))]
    z = [Variable_define("z", Operation(ArithmeticOperator.add, [Variable("x"), Variable("y")]))]
    instances = x + y + z
    program = "".join(f"{myClorm.pytocl(instance)}." for instance in instances)

    ctrl = clingo.Control()
    constraint_handler.add_to_control(ctrl)
    ctrl.add(program)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        model = solve_handle.model()
        values = set(myClorm.findInModel(model, Value).values())

    assert values == {
        Value("x", Val(BaseType.int, 5)),
        Value("y", Val(BaseType.int, 5)),
        Value("z", Val(BaseType.int, 10)),
    }


def test_nondet():
    x = [Variable_declare("x", FromFacts)] + [Variable_domain("x", Val(BaseType.int, value)) for value in range(5)]
    y = [
        Variable_define(
            "y",
            Operation(ArithmeticOperator.add, [Variable("x"), Val(BaseType.int, 3)]),
        )
    ]
    ensure = [Ensure(Operation(ComparisonOperator.neq, [Variable("y"), Val(BaseType.int, 6)]))]
    instances = x + y + ensure
    program = "".join(f"{myClorm.pytocl(instance)}." for instance in instances)

    ctrl = clingo.Control("0")
    constraint_handler.add_to_control(ctrl)
    ctrl.add(program)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        models = {frozenset(myClorm.findInModel(model, Value).values()) for model in solve_handle}

    assert models == {
        frozenset({Value("x", Val(BaseType.int, 0)), Value("y", Val(BaseType.int, 3))}),
        frozenset({Value("x", Val(BaseType.int, 1)), Value("y", Val(BaseType.int, 4))}),
        frozenset({Value("x", Val(BaseType.int, 2)), Value("y", Val(BaseType.int, 5))}),
        frozenset({Value("x", Val(BaseType.int, 4)), Value("y", Val(BaseType.int, 7))}),
    }


def test_optimization():
    x = [Variable_declare("x", FromFacts)] + [Variable_domain("x", Val(BaseType.int, value)) for value in range(5)]
    y = [
        Variable_define("y", Val(BaseType.float, 3.14)),
    ]
    opti = [Optimize_maximizeSum(Operation(ArithmeticOperator.add, [Variable("x"), Variable("y")]), label="price")]
    instances = x + y + opti
    program = "".join(f"{myClorm.pytocl(instance)}." for instance in instances)

    ctrl = clingo.Control("0")
    constraint_handler.add_to_control(ctrl)
    ctrl.add(program)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        for model in solve_handle:
            pass
            # print(myClorm.findInModel(model, Value).values())
    best_assignment = {x.name: x.val.value for x in myClorm.findInModel(model, Value).values()}
    print(myClorm.findInModel(model, Optimize_value).values())
    opt_value = {x.label: x.total.value for x in myClorm.findInModel(model, Optimize_value).values()}
    actual_value = {x.label: x.total.value for x in myClorm.findInModel(model, Optimize_modelValue).values()}

    assert best_assignment == {"x": 4, "y": 3.14}
    assert opt_value == {"price": 7}
    assert actual_value == {"price": 7.140000000000001}
