import ast
import hashlib
import itertools
import math
from types import CodeType
from typing import Any, Dict, List

from clingo import Symbol
from clingo.symbol import SymbolType

from flat_ch.core.serialization import clingo_to_python, python_to_clingo
from flat_ch.core.types import Type


class FailIntegrity(Exception):
    pass


DEFAULT_GLOBALS: Dict[str, Any] = {"FailIntegrity": FailIntegrity, "math": math}


def set_default_globals(globals_map: Dict[str, Any]) -> None:
    DEFAULT_GLOBALS.clear()
    DEFAULT_GLOBALS["FailIntegrity"] = FailIntegrity
    DEFAULT_GLOBALS["math"] = math
    DEFAULT_GLOBALS.update(globals_map)


class PythonIOVisitor(ast.NodeVisitor):
    def __init__(self):
        self.inputs = set()
        self.outputs = set()

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load):
            self.inputs.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.outputs.add(node.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        if isinstance(node.target, ast.Name):
            self.inputs.add(node.target.id)
            self.outputs.add(node.target.id)
        self.visit(node.value)


def infer_python_io(script_payload: str) -> tuple[list[str], list[str]]:
    """
    Parses the python script string and infers its inputs and outputs.
    Returns: (list_of_inputs, list_of_outputs)
    """
    try:
        syntax_tree = ast.parse(script_payload, mode="exec")
        visitor = PythonIOVisitor()
        visitor.visit(syntax_tree)
        return list(visitor.inputs), list(visitor.outputs)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse Python payload sequence: {e}")


class PythonProgram:
    code: CodeType
    target: str
    inputs: dict[int, list[str]]


class PythonRegistry:
    def __init__(self):
        self._program_id = itertools.count()

        self._programs: Dict[int, PythonProgram] = {}
        self._lookup: Dict[str, int] = {}
        self._expr_to_program: Dict[int, int] = {}

        self._context_stack: List[int] = []

    def register_program(self, script_payload: str, target_output: str) -> int:
        """
        Compiles the script once and provisions a tracking state object.
        Returns a unique program_id.
        """
        semantic_hash = hashlib.md5(f"{script_payload}::{target_output}".encode()).hexdigest()

        if semantic_hash in self._lookup:
            program_id = self._lookup[semantic_hash]
            self._context_stack.append(program_id)
            return program_id

        program_id = next(self._program_id)

        compiled_code = compile(script_payload, f"<py_macro_{program_id}>", "exec")

        program = PythonProgram()
        program.code = compiled_code
        program.target = target_output
        program.inputs = {}

        self._programs[program_id] = program
        self._lookup[semantic_hash] = program_id
        self._context_stack.append(program_id)
        return program_id

    def add_input_to_current(self, variable_name: str, expression_id: int) -> None:
        if self._context_stack:
            current_program = self._context_stack[-1]
            program = self._programs[current_program]
            program.inputs.setdefault(expression_id, []).append(variable_name)

    def finalize_current(self, expr_id: int) -> None:
        if self._context_stack:
            current_program = self._context_stack.pop()
            self._expr_to_program[expr_id] = current_program

    def execute(self, operation_id_symbol: Symbol, argument_list) -> Symbol:
        operation_id = operation_id_symbol.number
        program_id = self._expr_to_program[operation_id]
        program = self._programs[program_id]

        local_scope = {}
        current_node = argument_list

        while current_node and hasattr(current_node, "arguments") and len(current_node.arguments) == 2:
            head = current_node.arguments[0]
            current_node = current_node.arguments[1]

            arg_expr_id = head.arguments[0].number

            typed_value = head.arguments[1]
            arg_type = Type(typed_value.arguments[0].number)
            if arg_type == Type.FAIL:
                fail_value = typed_value.arguments[1]
                pure_val = fail_value.string if fail_value.type == SymbolType.String else str(fail_value)
                return python_to_clingo(Type.FAIL, pure_val)

            arg_type, pure_val = clingo_to_python(typed_value)
            if arg_type == Type.FAIL:
                return python_to_clingo(Type.FAIL, pure_val)

            if arg_expr_id in program.inputs:
                for var_name in program.inputs[arg_expr_id]:
                    local_scope[var_name] = pure_val

        result_type, result_value = self._execute_program(program, local_scope)
        result = python_to_clingo(result_type, result_value)
        return result

    def execute_current_directly(
        self, constant_args: list[tuple[Type, Any]], argument_ids: list[int]
    ) -> tuple[Type, Any]:
        """
        Executes the current active program context directly and removes it from the parsing stack.

        This is used during constant folding to remove the Python operation from the expression tree
        and replace it with its resulting value.
        """
        if not self._context_stack:
            raise IndexError("No active Python program context to execute directly.")

        program_id = self._context_stack.pop()
        program = self._programs[program_id]

        local_scope = {}

        for arg_id, (arg_type, pure_val) in zip(argument_ids, constant_args):
            if arg_type == Type.FAIL:
                return Type.FAIL, pure_val
            if arg_id in program.inputs:
                for var_name in program.inputs[arg_id]:
                    local_scope[var_name] = pure_val

        return self._execute_program(program, local_scope)

    def _execute_program(self, program: PythonProgram, local_scope: Dict[str, Any]) -> tuple[Type, Any]:
        try:
            exec(program.code, dict(DEFAULT_GLOBALS), local_scope)
        except FailIntegrity as error:
            return Type.FAIL, str(error)
        except Exception as error:
            return Type.FAIL, f"pythonError: {error}"

        result_value = local_scope.get(program.target)

        if result_value is None:
            result_type = Type.NONE
        elif isinstance(result_value, bool):
            result_type = Type.BOOL
        elif isinstance(result_value, int):
            result_type = Type.INT
        elif isinstance(result_value, float):
            result_type = Type.FLOAT
        elif isinstance(result_value, (set, frozenset)):
            result_type = Type.SET
        else:
            result_type = Type.STRING
            result_value = str(result_value)

        return result_type, result_value
