from __future__ import annotations

import itertools

import clingo

from flat_ch.core.domain import (
    EnsureConstraint,
    ExecutionDeclare,
    ExecutionStatement,
    Expression,
    ExprKind,
    IAssertStatement,
    IAssignStatement,
    IBind,
    IIfStatement,
    IOperation,
    IPair,
    IPythonOperation,
    IPythonStatement,
    IValue,
    IVariableDefine,
    IVariableRef,
    ProgramInput,
    StatementKind,
    Type,
)
from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.evaluation.python import infer_python_io


def _identifier_name(var_name: str | clingo.Symbol) -> str:
    if isinstance(var_name, str):
        return var_name
    if var_name.type == clingo.SymbolType.String:
        return var_name.string
    if var_name.type == clingo.SymbolType.Function and not var_name.arguments:
        return var_name.name
    return str(var_name)


def _exec_var_symbol(var_name: str | clingo.Symbol) -> clingo.Symbol:
    if isinstance(var_name, clingo.Symbol):
        return var_name
    return clingo.Function(var_name, [])


def _make_exec_sym(exec_name: str | clingo.Symbol, var_name: str | clingo.Symbol, direction: str) -> clingo.Symbol:
    """Constructs lowered 3-tuple symbol (EXEC, VAR, in/out)."""
    return clingo.Function(
        "",
        [
            _exec_var_symbol(exec_name),
            _exec_var_symbol(var_name),
            clingo.Function(direction, []),
        ],
    )


class SSA:
    """Transforms imperative execution blocks into pure functional IR expressions."""

    def apply(self, execution: ExecutionDeclare) -> list[ProgramInput]:
        state: dict[str, Expression] = {}
        self._assert_counter = itertools.count(0)
        self._execution_name = execution.name

        for input_var in execution.inputs:
            input_sym = _make_exec_sym(self._execution_name, input_var, "in")
            state[_identifier_name(input_var)] = IVariableRef(input_sym)

        try:
            for statement in execution.statements:
                state = self._handle_statement(statement, state)
        except ValueError as e:
            print(f"Error during SSA transformation for `{self._execution_name}`: {e}")
            return []

        outputs: list[ProgramInput] = []

        for output_var in execution.outputs:
            output_sym = _make_exec_sym(self._execution_name, output_var, "out")
            expr = state.get(_identifier_name(output_var), SSA._none_value())
            outputs.append(IVariableDefine(output_sym, expr))

        for key, expr in state.items():
            if key.startswith("_ssa"):
                outputs.append(EnsureConstraint(key, expr))

        return outputs

    @staticmethod
    def _none_value() -> Expression:
        return IValue(Type.NONE, None)

    @staticmethod
    def _fail_value(message: str) -> Expression:
        return IValue(Type.FAIL, message)

    @staticmethod
    def _bool_true_value() -> Expression:
        return IValue(Type.BOOL, True)

    def _handle_statement(self, statement: ExecutionStatement, state: dict[str, Expression]) -> dict[str, Expression]:
        match statement.kind:
            case StatementKind.ASSIGN:
                stmt: IAssignStatement = statement  # type: ignore
                state[stmt.variable] = self._substitution(stmt.expression, state)
                return state

            case StatementKind.IF:
                stmt_if: IIfStatement = statement  # type: ignore
                cond_sub = self._substitution(stmt_if.condition, state)

                then_state = state.copy()
                else_state = state.copy()

                for s in stmt_if.then_branch:
                    then_state = self._handle_statement(s, then_state)
                for s in stmt_if.else_branch:
                    else_state = self._handle_statement(s, else_state)

                all_variables = tuple(dict.fromkeys((*then_state.keys(), *else_state.keys())))

                for variable in all_variables:
                    then_val = then_state.get(variable)
                    else_val = else_state.get(variable)

                    if then_val == else_val and then_val is not None:
                        state[variable] = then_val
                    else:
                        default_val = (
                            self._bool_true_value()
                            if variable.startswith("_ssa")
                            else state.get(variable, self._none_value())
                        )
                        then_branch = then_val if then_val is not None else default_val
                        else_branch = else_val if else_val is not None else default_val

                        state[variable] = IOperation(Operator.ITE, (cond_sub, then_branch, else_branch))
                return state

            case StatementKind.ASSERT:
                stmt_assert: IAssertStatement = statement  # type: ignore
                cond_sub = self._substitution(stmt_assert.condition, state)
                assert_key = f"_ssa_{self._execution_name}_assert_{next(self._assert_counter)}"
                state[assert_key] = cond_sub
                return state

            case StatementKind.NOOP:
                return state

            case StatementKind.PYTHON:
                stmt_py: IPythonStatement = statement  # type: ignore
                python_string = stmt_py.code
                inferred_inputs, inferred_outputs = infer_python_io(python_string)

                required_inputs = list(
                    dict.fromkeys(
                        [
                            *inferred_inputs,
                            *(var for var in inferred_outputs if var in state),
                        ]
                    )
                )

                bound_inputs: list[IBind] = []
                for var_name in required_inputs:
                    if var_name not in state:
                        continue
                    sub_expr = self._substitution(IVariableRef(var_name), state)
                    bound_inputs.append(IBind(var_name, sub_expr))

                args_tuple = tuple(bound_inputs)

                if not inferred_outputs:
                    synthetic_expr = IPythonOperation(
                        code=python_string,
                        arguments=args_tuple,
                        outputs=("__python_effect",),
                    )
                    assert_key = f"_ssa_{self._execution_name}_python_{next(self._assert_counter)}"
                    state[assert_key] = IOperation(Operator.EQ, (synthetic_expr, self._none_value()))
                    return state

                for var_name in inferred_outputs:
                    state[var_name] = IPythonOperation(
                        code=python_string,
                        arguments=args_tuple,
                        outputs=(var_name,),
                    )

                return state

            case _:
                raise ValueError(f"Unknown statement kind: {statement.kind}")

    def _substitution(self, expression: Expression, state: dict[str, Expression]) -> Expression:
        match expression.kind:
            case ExprKind.VARIABLE:
                expr_var: IVariableRef = expression  # type: ignore
                var_key = _identifier_name(expr_var.name)
                if var_key not in state:
                    return self._fail_value(f"undefined variable: {expr_var.name}")
                return state[var_key]

            case ExprKind.OPERATION:
                expr_op: IOperation = expression  # type: ignore
                substituted_args = tuple(self._substitution(arg, state) for arg in expr_op.arguments)
                return IOperation(expr_op.operator, substituted_args)

            case ExprKind.PYTHON_OPERATION:
                expr_py_op: IPythonOperation = expression  # type: ignore
                substituted_bindings = tuple(
                    IBind(
                        b.name,
                        self._substitution(b.expression, state),
                    )
                    for b in expr_py_op.arguments
                )
                return IPythonOperation(
                    code=expr_py_op.code,
                    arguments=substituted_bindings,
                    outputs=expr_py_op.outputs,
                )

            case ExprKind.BIND:
                expr_bind: IBind = expression  # type: ignore
                return IBind(
                    expr_bind.name,
                    self._substitution(expr_bind.expression, state),
                )

            case ExprKind.PAIR:
                expr_pair: IPair = expression  # type: ignore
                return IPair(
                    self._substitution(expr_pair.key, state),
                    self._substitution(expr_pair.value, state),
                )

            case ExprKind.VALUE:
                return expression

            case _:
                raise ValueError(f"Unknown expression kind: {expression.kind}")
