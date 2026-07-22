from __future__ import annotations

import ast
import itertools
import math
from collections import Counter
from dataclasses import dataclass
from threading import Lock
from types import CodeType
from typing import Any

from clingo import Symbol
from clingo.symbol import SymbolType

try:
    import constraint_handler.solver_environment as constraint_solver_environment
except ImportError:
    constraint_solver_environment = None

from flat_ch.core.serialization import SerializerProtocol, normalize_float_str
from flat_ch.core.types import Type

_PYTHON_CODE_USAGE_COUNTER: Counter[str] = Counter()
_PYTHON_NUMERIC_INPUT_USAGE_COUNTER: Counter[tuple[str, tuple[tuple[str, int | str], ...]]] = Counter()
_PYTHON_USAGE_LOCK = Lock()


def reset_python_usage_counts() -> None:
    with _PYTHON_USAGE_LOCK:
        _PYTHON_CODE_USAGE_COUNTER.clear()
        _PYTHON_NUMERIC_INPUT_USAGE_COUNTER.clear()


def get_python_code_usage_counts() -> dict[str, int]:
    with _PYTHON_USAGE_LOCK:
        return dict(_PYTHON_CODE_USAGE_COUNTER)


def get_python_numeric_input_usage_counts() -> dict[tuple[str, tuple[tuple[str, int | str], ...]], int]:
    with _PYTHON_USAGE_LOCK:
        return dict(_PYTHON_NUMERIC_INPUT_USAGE_COUNTER)


def _normalize_numeric_inputs(values: list[Any]) -> tuple[tuple[str, int | str], ...] | None:
    normalized: list[tuple[str, int | str]] = []
    for value in values:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            normalized.append(("int", value))
            continue
        if isinstance(value, float):
            normalized.append(("float", normalize_float_str(value)))
            continue
        return None
    return tuple(normalized)


def _record_python_usage(code: str, values: list[Any]) -> None:
    numeric_inputs = _normalize_numeric_inputs(values)
    with _PYTHON_USAGE_LOCK:
        _PYTHON_CODE_USAGE_COUNTER[code] += 1
        if numeric_inputs is not None:
            _PYTHON_NUMERIC_INPUT_USAGE_COUNTER[(code, numeric_inputs)] += 1


class FailIntegrity(Exception):
    """Exception raised by user Python scripts to indicate an integrity failure."""


_FAIL_INTEGRITY_EXCEPTIONS: tuple[type[Exception], ...] = (FailIntegrity,)
if constraint_solver_environment is not None:
    _FAIL_INTEGRITY_EXCEPTIONS = _FAIL_INTEGRITY_EXCEPTIONS + (constraint_solver_environment.FailIntegrityExn,)


DEFAULT_GLOBALS: dict[str, Any] = {
    "FailIntegrity": FailIntegrity,
    "math": math,
    "pow": math.pow,
}
if constraint_solver_environment is not None:
    DEFAULT_GLOBALS["solver_environment"] = constraint_solver_environment
    DEFAULT_GLOBALS["FailIntegrityExn"] = constraint_solver_environment.FailIntegrityExn


def set_default_globals(globals_map: dict[str, Any]) -> None:
    """Updates the global scope available to executed Python snippets."""
    DEFAULT_GLOBALS.clear()
    DEFAULT_GLOBALS["FailIntegrity"] = FailIntegrity
    DEFAULT_GLOBALS["math"] = math
    DEFAULT_GLOBALS["pow"] = math.pow
    DEFAULT_GLOBALS.update(globals_map)


class PythonIOVisitor(ast.NodeVisitor):
    """AST Visitor that extracts referenced input variables and target outputs."""

    def __init__(self) -> None:
        self.inputs: dict[str, None] = {}
        self.outputs: dict[str, None] = {}

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.inputs.setdefault(node.id, None)
        elif isinstance(node.ctx, ast.Store):
            self.outputs.setdefault(node.id, None)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name):
            self.inputs.setdefault(node.target.id, None)
            self.outputs.setdefault(node.target.id, None)
        self.visit(node.value)


def infer_python_io(script_payload: str) -> tuple[list[str], list[str]]:
    """Parses a Python snippet and infers referenced inputs and assigned outputs."""
    try:
        syntax_tree = ast.parse(script_payload, mode="exec")
        visitor = PythonIOVisitor()
        visitor.visit(syntax_tree)

        builtin_names = set(DEFAULT_GLOBALS.keys()) | set(dir(__builtins__))
        inferred_inputs = [var for var in visitor.inputs.keys() if var not in builtin_names]
        inferred_outputs = list(visitor.outputs.keys())

        return inferred_inputs, inferred_outputs
    except SyntaxError as e:
        raise ValueError(f"Failed to parse Python payload snippet: {e}") from e


@dataclass(frozen=True, slots=True)
class CompiledPythonProgram:
    program_id: int
    code: CodeType
    target_output: str
    source: str


class PythonRegistry:
    """Compiles, caches, and executes Python code snippets referenced by IR nodes."""

    def __init__(self, serializer: SerializerProtocol | None = None) -> None:
        self.serializer = serializer
        self._id_gen = itertools.count(1)
        self._lookup: dict[str, CompiledPythonProgram] = {}
        self._id_to_program: dict[int, CompiledPythonProgram] = {}
        self._expr_to_program: dict[int, int] = {}
        self._expr_to_arg_names: dict[int, list[str]] = {}

    def set_serializer(self, serializer: SerializerProtocol) -> None:
        """Sets or updates the serializer instance used for symbol conversion."""
        self.serializer = serializer

    def register_program(self, script_payload: str, target_output: str = "__fch_result") -> int:
        """Compiles a Python snippet (if not cached) and returns a unique integer program_id."""
        semantic_key = f"{script_payload}::{target_output}"

        if semantic_key in self._lookup:
            return self._lookup[semantic_key].program_id

        program_id = next(self._id_gen)
        compiled_code = compile(script_payload, filename=f"<fch_python_{program_id}>", mode="exec")

        program = CompiledPythonProgram(
            program_id=program_id,
            code=compiled_code,
            target_output=target_output,
            source=script_payload,
        )

        self._lookup[semantic_key] = program
        self._id_to_program[program_id] = program
        return program_id

    def link_expr_to_program(self, expr_id: int, program_id: int, arg_names: list[str] | None = None) -> None:
        """Associates an expression ID with a registered python program ID and optional parameter names."""
        self._expr_to_program[expr_id] = program_id
        if arg_names:
            self._expr_to_arg_names[expr_id] = arg_names

    def execute(self, operation_id_symbol: Symbol, argument_list: Symbol) -> Symbol:
        """
        Clingo Python callback function.
        Unpacks incoming Clingo argument terms, executes the Python snippet,
        and returns a serialized Clingo Symbol.
        """
        if self.serializer is None:
            raise RuntimeError("PythonRegistry requires a serializer to execute Clingo terms.")

        operation_id = operation_id_symbol.number
        program_id = self._expr_to_program.get(operation_id, operation_id)
        program = self._id_to_program.get(program_id)

        if program is None:
            return self.serializer.python_to_clingo(Type.FAIL, f"Unregistered Python operation ID: {operation_id}")

        unpacked_args: list[tuple[str | None, Any]] = []
        current_node = argument_list

        while current_node and current_node.type == SymbolType.Function and len(current_node.arguments) == 2:
            head = current_node.arguments[0]
            current_node = current_node.arguments[1]

            var_name, typed_value = self._extract_bound_argument(head)

            arg_type, pure_val = self.serializer.clingo_to_python(typed_value)
            if arg_type == Type.FAIL:
                return self.serializer.python_to_clingo(Type.FAIL, pure_val)

            unpacked_args.append((var_name, pure_val))

        registered_arg_names = self._expr_to_arg_names.get(operation_id, [])

        if len(unpacked_args) == len(registered_arg_names) and len(unpacked_args) > 1:
            if all(name is None for name, _ in unpacked_args):
                unpacked_args.reverse()

        local_scope: dict[str, Any] = {}
        for arg_idx, (var_name, pure_val) in enumerate(unpacked_args):
            if not var_name:
                if arg_idx < len(registered_arg_names):
                    var_name = registered_arg_names[arg_idx]
                else:
                    var_name = f"_fch_arg_{arg_idx + 1}"

            local_scope[var_name] = pure_val

        _record_python_usage(program.source, list(local_scope.values()))

        result_type, result_value = self._run_compiled(program, local_scope)
        return self.serializer.python_to_clingo(result_type, result_value)

    def _extract_bound_argument(self, head: Symbol) -> tuple[str | None, Symbol]:
        var_name = None
        typed_value = head

        if typed_value.type == SymbolType.Function and typed_value.name == "bind" and len(typed_value.arguments) == 2:
            var_name = (
                typed_value.arguments[0].string
                if typed_value.arguments[0].type == SymbolType.String
                else str(typed_value.arguments[0])
            )
            typed_value = typed_value.arguments[1]

        if (
            typed_value.type == SymbolType.Function
            and typed_value.name == ""
            and len(typed_value.arguments) == 2
            and typed_value.arguments[0].type == SymbolType.Number
        ):
            return var_name, typed_value.arguments[1]

        return var_name, typed_value

    def execute_directly(
        self,
        program_id: int,
        constant_args: list[tuple[Type, Any]],
        arg_names: list[str] | None = None,
    ) -> tuple[Type, Any]:
        """
        Executes a registered Python program directly with Python primitive values.
        Used during constant folding to simplify Python operations in the AST.
        """
        program = self._id_to_program.get(program_id)
        if program is None:
            return Type.FAIL, f"Unregistered Python program ID: {program_id}"

        local_scope: dict[str, Any] = {}
        for idx, (arg_type, pure_val) in enumerate(constant_args):
            if arg_type == Type.FAIL:
                return Type.FAIL, pure_val

            var_name = arg_names[idx] if arg_names and idx < len(arg_names) else f"_fch_arg_{idx + 1}"
            local_scope[var_name] = pure_val

        return self._run_compiled(program, local_scope)

    def _run_compiled(self, program: CompiledPythonProgram, local_scope: dict[str, Any]) -> tuple[Type, Any]:
        """Executes bytecode with global scope and extracts result."""
        execution_scope = dict(DEFAULT_GLOBALS)
        execution_scope.update(local_scope)

        try:
            exec(program.code, execution_scope)
        except _FAIL_INTEGRITY_EXCEPTIONS as error:
            return Type.FAIL, str(error)
        except Exception as error:
            return Type.FAIL, f"pythonError: {error}"

        result_value = execution_scope.get(program.target_output)

        if result_value is None:
            return Type.NONE, None
        elif isinstance(result_value, bool):
            return Type.BOOL, result_value
        elif isinstance(result_value, int):
            return Type.INT, result_value
        elif isinstance(result_value, float):
            return Type.FLOAT, result_value
        elif isinstance(result_value, (set, frozenset)):
            return Type.SET, result_value
        else:
            return Type.STRING, str(result_value)
