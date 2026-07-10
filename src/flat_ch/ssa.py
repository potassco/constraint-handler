from __future__ import annotations
from enum import Enum
import itertools

from clingo import Function, String, Symbol, SymbolType

from flat_ch.operators.python import infer_python_io
from flat_ch.utils import symbol_name

class Statement(str, Enum):
    """
    The different types of facts that can be emitted by the flattener.
    """
    ASSIGN = "assign"
    ASSERT = "assert"
    IF = "if"
    NOOP = "noop"
    PYTHON = "python"
    

class SSA:
    def __init__(self):
        pass

    def apply(self, execution):
        state: dict[str, Symbol] = {}
        self._assert_counter = itertools.count(0)


        name_symbol, statements_tuple, inputs_tuple, outputs_tuple = execution.arguments
        self._execution_name = symbol_name(name_symbol)

        statements = SSA._unpack_flat_tuple(statements_tuple)
        input_symbols = SSA._unpack_flat_tuple(inputs_tuple)
        output_symbols = SSA._unpack_flat_tuple(outputs_tuple)

        for input_symbol in input_symbols:
            symbol = Function("variable", [
                Function("",[
                    name_symbol,
                    input_symbol,
                    Function("in", [])
                ])
            ])
            state[symbol_name(input_symbol)] = symbol

        try:
            for statement in statements:
                state = self._handle_statement(statement, state)
        except ValueError as e:
            print("Error during SSA transformation for `", self._execution_name,"`: ", e, sep="")
            return []

        outputs = []

        for output_symbol in output_symbols:
            variable_name = symbol_name(output_symbol)

            if variable_name not in state:
                raise ValueError(f"Variable '{variable_name}' was expected as output but is never defined.")

            symbol = Function("",[
                    name_symbol,
                    output_symbol,
                    Function("out", [])
            ])

            outputs.append(Function(
                "variable_define",
                [
                    symbol,
                    state[variable_name]
                ]
            ))

        for key, expression in state.items():
            if key.startswith("_ssa"):
                outputs.append(
                    Function("ensure",
                        [
                            Function(key,[]),
                            expression
                        ]
                    )
                )

        return outputs

    @staticmethod
    def _none_value() -> Symbol:
        return Function("val", [Function("none", []), Function("none", [])])

    def _handle_statement(self, statement, state):
        match Statement(statement.name):
            case Statement.ASSIGN:
                variable_symbol, expression = statement.arguments
                state[symbol_name(variable_symbol)] = SSA._substitution(expression, state)
                return state
            case Statement.IF:
                if_condition, then_statements_tuple, else_statements_tuple = statement.arguments

                if_condition_substituted = SSA._substitution(if_condition, state)

                then_statements = SSA._unpack_flat_tuple(then_statements_tuple)
                else_statements = SSA._unpack_flat_tuple(else_statements_tuple)

                then_state = state.copy()
                else_state = state.copy()

                for then_statement in then_statements:
                    then_state = self._handle_statement(then_statement, then_state)
                for else_statement in else_statements:
                    else_state = self._handle_statement(else_statement, else_state)
                
                all_variables: list[str] = set(then_state.keys()) | set(else_state.keys())

                for variable in all_variables:
                    then_value = then_state.get(variable)
                    else_value = else_state.get(variable)

                    if then_value == else_value:
                        new_value = then_value
                    else:
                        if variable.startswith("_ssa"):
                            old_value = Function("val", [
                                Function("bool",[]),
                                Function("true",[])
                            ])
                        else:
                            old_value = state.get(variable, SSA._none_value())
                        then_branch = old_value
                        else_branch = old_value

                        if then_value is not None:
                            then_branch = then_value

                        if else_value is not None:
                            else_branch = else_value

                        new_value = Function("operation", [
                                Function("ite", []),
                                Function("", [
                                    if_condition_substituted,
                                    then_branch,
                                    else_branch
                                ])
                        ])
                    
                    state[variable] = new_value
                return state
            case Statement.ASSERT:
                condition = statement.arguments[0]
                condition_substituted = SSA._substitution(condition, state)

                name = f"_ssa_{self._execution_name}_assert_{next(self._assert_counter)}"

                state[name] = condition_substituted
                return state

            case Statement.NOOP:
                return state
            case Statement.PYTHON:
                python_string = statement.arguments[0].string

                inferred_inputs, inferred_outputs = infer_python_io(python_string)

                bound_inputs = []
                for var_name in inferred_inputs:
                    if var_name not in state:
                        continue
                        
                    input_expr = Function("variable", [Function(var_name, [])])
                    substituted_input = SSA._substitution(input_expr, state)
                    
                    bound_inputs.append(
                        Function("bind", [String(var_name), substituted_input])
                    )

                args_tuple = Function("", bound_inputs)

                if not inferred_outputs:
                    synthetic_expr = Function("operation", [
                        Function("python", [String(python_string), String("__python_effect")]),
                        args_tuple
                    ])

                    state[f"_ssa_{self._execution_name}_python_{next(self._assert_counter)}"] = Function(
                        "operation",
                        [
                            Function("eq", []),
                            Function("", [
                                synthetic_expr,
                                SSA._none_value(),
                            ])
                        ]
                    )
                    return state

                for var_name in inferred_outputs:
                    state[var_name] = Function("operation", [
                        Function("python", [String(python_string), String(var_name)]),
                        args_tuple
                    ])

                return state
            case _:
                return state

    @staticmethod
    def _substitution(expression, state):
        match expression.name:
            case "operation":
                arguments = SSA._unpack_flat_tuple(expression.arguments[1])
    
                return Function("operation", [
                    expression.arguments[0],
                    Function("", [SSA._substitution(argument, state) for argument in arguments])
                    ])

            case "variable":
                variable_symbol = expression.arguments[0]
                variable_name = symbol_name(variable_symbol)

                if variable_name not in state:
                    raise ValueError(f"Variable '{variable_symbol}' is not defined in the current state.")

                return state[variable_name]
        return expression

    @staticmethod
    def _unpack_flat_tuple(term: Symbol) -> list[str]:
        if term.type != SymbolType.Function:
            return []

        if term.name == "":
            return list(term.arguments)
            
        return [term]