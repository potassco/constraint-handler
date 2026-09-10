import clingo

import constraint_handler
import constraint_handler.schemas.atom as atom
from constraint_handler.schemas.atom import (
    Ensure,
    Optimize_maximizeSum,
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
    input = [
        Variable_define("x", Val(BaseType.int, 5)),
        Variable_define("y", Variable("x")),
        Variable_define("z", Operation(ArithmeticOperator.add, [Variable("x"), Variable("y")])),
    ]

    ctrl = clingo.Control()
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_declarations(ctrl, input)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        model = solve_handle.model()
        values = set(constraint_handler.find_values(model).values())

    assert values == {
        Value("x", Val(BaseType.int, 5)),
        Value("y", Val(BaseType.int, 5)),
        Value("z", Val(BaseType.int, 10)),
    }


def test_nondet():
    xdeclare = Variable_declare("x", FromFacts)
    xdomain = [Variable_domain("x", Val(BaseType.int, value)) for value in range(5)]
    ydefine = Variable_define(
        "y",
        Operation(ArithmeticOperator.add, [Variable("x"), Val(BaseType.int, 3)]),
    )
    ensure = Ensure(Operation(ComparisonOperator.neq, [Variable("y"), Val(BaseType.int, 6)]))
    instance = [xdeclare, ydefine, ensure] + xdomain

    ctrl = clingo.Control("0")
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_declarations(ctrl, instance)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        models = {frozenset(constraint_handler.find_values(model).values()) for model in solve_handle}

    assert models == {
        frozenset({Value("x", Val(BaseType.int, 0)), Value("y", Val(BaseType.int, 3))}),
        frozenset({Value("x", Val(BaseType.int, 1)), Value("y", Val(BaseType.int, 4))}),
        frozenset({Value("x", Val(BaseType.int, 2)), Value("y", Val(BaseType.int, 5))}),
        frozenset({Value("x", Val(BaseType.int, 4)), Value("y", Val(BaseType.int, 7))}),
    }


def test_optimization():
    xdeclar = Variable_declare("x", FromFacts)
    xdomain = [Variable_domain("x", Val(BaseType.int, value)) for value in range(5)]
    ydefine = Variable_define("y", Val(BaseType.float, 3.25))
    optimiz = Optimize_maximizeSum(Operation(ArithmeticOperator.add, [Variable("x"), Variable("y")]), label="price")
    instance = [xdeclar, ydefine, optimiz] + xdomain

    ctrl = clingo.Control("0")
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_declarations(ctrl, instance)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        for model in solve_handle:
            pass

    best_assignment = {}
    opt_value = {}
    actual_value = {}
    for x in constraint_handler.find_values(model).values():
        match x:
            case atom.Value():
                best_assignment[x.name] = x.val.value
            case atom.Optimize_value():
                opt_value[x.label] = x.total.value
            case atom.Optimize_modelValue():
                actual_value[x.label] = x.total.value

    assert best_assignment == {"x": 4, "y": 3.25}
    assert opt_value == {"price": 7}
    assert actual_value == {"price": 7.25}
