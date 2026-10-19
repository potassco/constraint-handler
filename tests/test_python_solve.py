import clingo

import constraint_handler
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.core as core
import constraint_handler.schemas.post as post
import constraint_handler.schemas.solve as solve
from constraint_handler.schemas.atom import Ensure, Variable_declare, Variable_define
from constraint_handler.schemas.domain import Definition
from constraint_handler.schemas.expression import TRUE, Operation, Val, Variable
from constraint_handler.schemas.operators import ArithmeticOperator, ComparisonOperator
from constraint_handler.schemas.result import Value
from constraint_handler.schemas.type_ import BaseType


def test_python_layer_handoffs():
    derived_label = clingo.Function("derived")
    y_definition = Operation(ArithmeticOperator.add, myClorm.ImmutableList([Variable("x"), Val(BaseType.int, 2)]))
    ensure_expression = Operation(ComparisonOperator.eq, myClorm.ImmutableList([Variable("y"), Val(BaseType.int, 7)]))
    instance = [
        Variable_declare("x", Definition()),
        Variable_define("x", Val(BaseType.int, 5)),
        Variable_declare("y", Definition(), derived_label),
        Variable_define("y", y_definition, label=derived_label),
        Ensure(ensure_expression),
    ]
    anonymous_core_declarations = {
        core.Engine_request(clingo.Function("compile")),
        core.Variable_declare("x", Definition()),
        core.Variable_define("x", Val(BaseType.int, 5), TRUE),
        core.Ensure(ensure_expression),
    }
    derived_core_declarations = {
        core.Variable_declare("y", Definition()),
        core.Variable_define("y", y_definition, TRUE),
    }
    expected_core_declarations = anonymous_core_declarations | derived_core_declarations

    ctrl = clingo.Control()
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_declarations(ctrl, instance)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        model = solve_handle.model()
        actual_core = set(constraint_handler.find_core(model).values())
        actual_derived_core = set(constraint_handler.find_core(model, derived_label).values())

    assert actual_core == expected_core_declarations
    assert actual_derived_core == derived_core_declarations

    anonymous_solve_declarations = {
        core.Variable_declare("x", Definition()),
        core.Variable_define("x", Val(BaseType.int, 5), TRUE),
        solve.Share_value(ensure_expression),
    }
    derived_solve_declarations = {
        core.Variable_declare("y", Definition()),
        core.Variable_define("y", y_definition, TRUE),
    }
    expected_solve_declarations = anonymous_solve_declarations | derived_solve_declarations
    anonymous_post_declarations = {
        post.Variable_interface("x"),
    }
    derived_post_declarations = {
        post.Variable_interface("y"),
    }
    expected_post_declarations = anonymous_post_declarations | derived_post_declarations

    ctrl = clingo.Control()
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_core(ctrl, anonymous_core_declarations)
    constraint_handler.add_core(ctrl, derived_core_declarations, derived_label)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        model = solve_handle.model()
        actual_solve = set(constraint_handler.find_solve(model).values())
        actual_derived_solve = set(constraint_handler.find_solve(model, derived_label).values())
        actual_post = set(constraint_handler.find_post(model).values())
        actual_derived_post = set(constraint_handler.find_post(model, derived_label).values())

    assert actual_solve == expected_solve_declarations
    assert actual_derived_solve == derived_solve_declarations
    assert actual_post == expected_post_declarations
    assert actual_derived_post == derived_post_declarations

    ctrl = clingo.Control()
    constraint_handler.add_to_control(ctrl)
    constraint_handler.add_solve(ctrl, anonymous_solve_declarations)
    constraint_handler.add_solve(ctrl, derived_solve_declarations, derived_label)
    constraint_handler.add_post(ctrl, anonymous_post_declarations)
    constraint_handler.add_post(ctrl, derived_post_declarations, derived_label)
    constraint_handler.add_core(ctrl, [core.Engine_request(clingo.Function("compile"))], derived_label)
    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        actual_values = set(constraint_handler.find_values(solve_handle.model()).values())

    assert actual_values == {
        Value("x", Val(BaseType.int, 5)),
        Value("y", Val(BaseType.int, 7)),
    }
