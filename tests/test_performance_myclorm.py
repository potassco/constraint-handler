from dataclasses import dataclass

import clingo
import pytest

import constraint_handler.myClorm as myClorm
import constraint_handler.python_externals.helper as python_helper
import constraint_handler.python_externals.interface as python_interface
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.propagator_atom as propagator_atom
import constraint_handler.schemas.type_ as type_
from constraint_handler.schemas.operators import ArithmeticOperator

MYCLORM_BATCH_SIZE = 100


@dataclass(frozen=True)
class BenchmarkSymbolicAtom:
    symbol: clingo.Symbol
    literal: int


class BenchmarkPropagateInit:
    def __init__(self, atoms: tuple[BenchmarkSymbolicAtom, ...]) -> None:
        self.symbolic_atoms = self
        self._atoms_by_signature = {}
        for atom in atoms:
            signature = (atom.symbol.name, len(atom.symbol.arguments))
            self._atoms_by_signature.setdefault(signature, []).append(atom)

    def by_signature(self, name: str, arity: int) -> tuple[BenchmarkSymbolicAtom, ...]:
        return tuple(self._atoms_by_signature.get((name, arity), ()))

    @staticmethod
    def solver_literal(literal: int) -> int:
        return literal


def make_expression(index: int) -> expression.Operation:
    shared = expression.Operation(
        ArithmeticOperator.add,
        myClorm.ImmutableList([expression.Variable(clingo.Function("x")), expression.Val(type_.BaseType.int, index)]),
    )
    distinct = expression.Operation(
        ArithmeticOperator.add,
        myClorm.ImmutableList(
            [expression.Variable(clingo.Function("y")), expression.Val(type_.BaseType.int, index + 1)]
        ),
    )
    for depth in range(4):
        distinct = expression.Operation(
            ArithmeticOperator.mult,
            myClorm.ImmutableList([shared, distinct, expression.Val(type_.BaseType.int, depth + 2)]),
        )
    return expression.Operation(ArithmeticOperator.add, myClorm.ImmutableList([shared, distinct, shared]))


preprocessing_inputs = tuple(
    (
        myClorm.pytocl(make_expression(index)),
        myClorm.pytocl(
            [
                (clingo.Function("x"), expression.Val(type_.BaseType.int, index)),
                (clingo.Function("y"), expression.Val(type_.BaseType.int, index + 1)),
            ]
        ),
        myClorm.pytocl([]),
        myClorm.pytocl([clingo.Function("x"), clingo.Function("y")]),
        myClorm.pytocl([expression.Val(type_.BaseType.int, index), expression.Val(type_.BaseType.int, index + 1)]),
        myClorm.pytocl([("x", type_.BaseType.int), ("y", type_.BaseType.int)]),
        clingo.String(f"result_{index} = x + y"),
        clingo.String(f"helper_{index} = x + y"),
        clingo.String(f"helper_{index} * 2"),
    )
    for index in range(MYCLORM_BATCH_SIZE)
)
propagator_init = BenchmarkPropagateInit(
    tuple(
        atom
        for index in range(MYCLORM_BATCH_SIZE)
        for atom in (
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_variable_define(
                        clingo.Function(f"variable_{index}"), make_expression(index), clingo.Function("benchmark")
                    )
                ),
                index * 7 + 1,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(propagator_atom.Propagator_ensure(make_expression(index), clingo.Function("benchmark"))),
                index * 7 + 2,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_share_value(make_expression(index), clingo.Function("benchmark"))
                ),
                index * 7 + 3,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_evaluate(
                        expression.Variable(clingo.Function(f"result_{index}")),
                        make_expression(index),
                        clingo.Function("benchmark"),
                    )
                ),
                index * 7 + 4,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_bool_evaluate(make_expression(index), clingo.Function("benchmark"))
                ),
                index * 7 + 5,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_set_assign(
                        clingo.Function(f"set_{index}"), make_expression(index), clingo.Function("benchmark")
                    )
                ),
                index * 7 + 6,
            ),
            BenchmarkSymbolicAtom(
                myClorm.pytocl(
                    propagator_atom.Propagator_multimap_assign(
                        clingo.Function(f"map_{index}"),
                        expression.Variable(clingo.Function("x")),
                        make_expression(index),
                        clingo.Function("benchmark"),
                    )
                ),
                index * 7 + 7,
            ),
        )
    )
)


def run_myclorm_preprocessing() -> None:
    myClorm.cltopy.cache_clear()
    for function in (
        python_helper.pythonListElements,
        python_helper.pythonReversedList,
        python_helper.pythonEnumerateElements,
        python_helper.pythonListLength,
        python_helper.pythonIsList,
        python_helper.pythonIsString,
        python_helper.pythonIsTuple,
        python_helper.pythonTupleElements,
        python_helper.pythonStringLength,
        python_helper.pythonReify,
        python_helper.pythonReflect,
        python_helper.pythonNestedToTuple,
        python_helper.pythonScopeToString,
        python_helper.pythonStringAdd,
        python_interface.pythonIsExpr,
        python_interface.pythonNormalExpr,
        python_interface.pythonExpressionVariable,
        python_interface.pythonEnumerateVariables,
        python_interface.pythonBetaReduction,
        python_interface.pythonEvalExpr,
        python_interface.pythonStatementVariables,
    ):
        getattr(function, "cache_clear", lambda: None)()
    for (
        expression_symbol,
        arguments,
        globals_id,
        variables,
        values,
        types,
        statement,
        extract_statement,
        extract_expr,
    ) in preprocessing_inputs:
        python_interface.pythonIsExpr(expression_symbol)
        python_interface.pythonNormalExpr(expression_symbol)
        python_interface.pythonExpressionVariable(expression_symbol)
        python_interface.pythonEnumerateVariables(expression_symbol)
        python_interface.pythonBetaReduction(expression_symbol, variables, values)
        python_interface.pythonEvalExpr(expression_symbol, arguments, globals_id)
        python_helper.pythonListElements(arguments)
        python_helper.pythonReversedList(arguments)
        python_helper.pythonEnumerateElements(arguments)
        python_helper.pythonListLength(arguments)
        python_helper.pythonIsList(arguments)
        python_helper.pythonIsString(statement)
        python_helper.pythonIsTuple(expression_symbol)
        python_helper.pythonTupleElements(arguments)
        python_helper.pythonStringLength(statement)
        python_helper.pythonReify(expression_symbol)
        python_helper.pythonReflect(clingo.Function("function"), clingo.Function("benchmark"), arguments)
        python_helper.pythonNestedToTuple(arguments)
        python_helper.pythonScopeToString(myClorm.pytocl([clingo.Function("scope")]), clingo.Function("x"))
        python_helper.pythonStringAdd(clingo.String("constraint"), clingo.String("handler"))
        python_interface.pythonStatementVariables(statement, types, globals_id)
        python_interface.pythonTypeExtract(extract_statement, extract_expr, types, globals_id)


def run_myclorm_propagator_init() -> None:
    myClorm.cltopy.cache_clear()
    for target in (
        propagator_atom.Propagator_variable_define,
        propagator_atom.Propagator_ensure,
        propagator_atom.Propagator_share_value,
        propagator_atom.Propagator_evaluate,
        propagator_atom.Propagator_bool_evaluate,
        propagator_atom.Propagator_set_assign,
        propagator_atom.Propagator_multimap_assign,
    ):
        myClorm.findInPropagateInit(propagator_init, target)


@pytest.mark.performance
def test_myclorm_preprocessing_performance(benchmark):
    benchmark.extra_info.update({"component": "myClorm", "workflow": "python externals preprocessing"})
    benchmark.pedantic(run_myclorm_preprocessing, rounds=5, iterations=1)
    assert benchmark.stats["mean"] <= 4.0


@pytest.mark.performance
def test_myclorm_propagator_init_performance(benchmark):
    benchmark.extra_info.update({"component": "myClorm", "workflow": "propagator initialization"})
    benchmark.pedantic(run_myclorm_propagator_init, rounds=5, iterations=1)
    assert benchmark.stats["mean"] <= 4.0
