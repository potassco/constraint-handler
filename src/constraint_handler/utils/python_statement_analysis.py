"""Analyze simple Python snippets and infer variable type sets."""

from __future__ import annotations

import ast
import builtins
import collections.abc as collections_abc
import inspect
import itertools
import types
import typing
from collections.abc import Mapping
from typing import NamedTuple

import clingo

from constraint_handler.utils.python_type_model import (
    DictOf,
    FunctionType,
    ListOf,
    RepeatedTupleOf,
    Scalar,
    SetOf,
    TupleOf,
    TypeInfo,
    UnknownType,
    UnsupportedType,
)
from constraint_handler.utils.python_type_signatures import (
    get_return_types,
    resolve_static_overloads,
)

_RUNTIME_MISSING = object()
_UNKNOWN_FUNCTION_TYPE = FunctionType(None, UnknownType)
_ORDERABLE_SCALAR_TYPES = frozenset({Scalar.BOOL, Scalar.INT, Scalar.FLOAT})


def _callable_annotation_to_function_types(annotation_args: tuple[object, ...]) -> frozenset[TypeInfo]:
    if len(annotation_args) != 2:
        return frozenset({_UNKNOWN_FUNCTION_TYPE})

    input_part, return_part = annotation_args
    return_types = _annotation_to_types(return_part)

    match input_part:
        case _ if input_part is Ellipsis:
            return frozenset(FunctionType(None, return_type) for return_type in return_types)
        case [*param_annotations] | (*param_annotations,):
            input_type_options = tuple(_annotation_to_types(param_ann) for param_ann in param_annotations)
            return frozenset(
                FunctionType(input_types, return_type)
                for input_types in itertools.product(*input_type_options)
                for return_type in return_types
            )
        case _:
            return frozenset({_UNKNOWN_FUNCTION_TYPE})


def _annotation_to_types(annotation: object) -> frozenset[TypeInfo]:
    origin = typing.get_origin(annotation)
    if origin in (types.UnionType, typing.Union):
        return frozenset().union(*(_annotation_to_types(arg) for arg in typing.get_args(annotation)))

    annotation_args = typing.get_args(annotation)
    arg_type_sets = tuple(_annotation_to_types(arg) for arg in annotation_args)
    dispatch = annotation if origin is None else origin
    match dispatch:
        case inspect.Signature.empty | typing.Any | builtins.object:
            return frozenset({UnknownType})
        case types.NoneType:
            return frozenset({Scalar.NONE})
        case builtins.bool:
            return frozenset({Scalar.BOOL})
        case builtins.int:
            return frozenset({Scalar.INT})
        case builtins.float:
            return frozenset({Scalar.FLOAT})
        case builtins.str:
            return frozenset({Scalar.STRING})
        case collections_abc.Callable:
            return _callable_annotation_to_function_types(typing.get_args(annotation))
        case builtins.list:
            return frozenset(
                ListOf(element_type)
                for element_type in (frozenset({UnknownType}) if not arg_type_sets else arg_type_sets[0])
            )
        case builtins.set:
            return frozenset(
                SetOf(element_type)
                for element_type in (frozenset({UnknownType}) if not arg_type_sets else arg_type_sets[0])
            )
        case builtins.dict:
            if len(arg_type_sets) == 2:
                key_types, value_types = arg_type_sets
                return frozenset(DictOf(key_type, value_type) for key_type in key_types for value_type in value_types)
            return frozenset({DictOf(UnknownType, UnknownType)})
        case builtins.tuple:
            if annotation_args[-1:] == (Ellipsis,):
                return frozenset(RepeatedTupleOf(element_type) for element_type in arg_type_sets[0])
            if not arg_type_sets:
                return frozenset({RepeatedTupleOf(UnknownType)})
            return frozenset(TupleOf(tuple(element_types)) for element_types in itertools.product(*arg_type_sets))
        case _:
            return frozenset({UnsupportedType})


def _callable_type_info(func: collections_abc.Callable) -> frozenset[TypeInfo]:
    input_type_options: tuple[frozenset[TypeInfo], ...] | None = None
    return_types: frozenset[TypeInfo] = frozenset({UnknownType})

    try:
        hints = typing.get_type_hints(func)
        return_types = _annotation_to_types(hints.get("return", inspect.Signature.empty))
    except Exception:
        hints = {}

    try:
        signature = inspect.signature(func)
        return_types = _annotation_to_types(hints.get("return", signature.return_annotation))
        if all(
            parameter.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            for parameter in signature.parameters.values()
        ):
            input_type_options = tuple(
                _annotation_to_types(hints.get(parameter.name, parameter.annotation))
                for parameter in signature.parameters.values()
            )
    except (TypeError, ValueError):
        pass

    if return_types == frozenset({UnknownType}):
        static_overloads = resolve_static_overloads(
            static_module_name=getattr(func, "__module__", None),
            static_function_name=getattr(func, "__name__", None),
        )
        if static_overloads:
            return static_overloads

    if input_type_options is None:
        return frozenset(FunctionType(None, return_type) for return_type in return_types)

    return frozenset(
        FunctionType(input_types, return_type)
        for input_types in itertools.product(*input_type_options)
        for return_type in return_types
    )


def _value_to_type(value: object) -> frozenset[TypeInfo]:
    match value:
        case _ if callable(value):
            return _callable_type_info(value)
        case None:
            return frozenset({Scalar.NONE})
        case bool():
            return frozenset({Scalar.BOOL})
        case int():
            return frozenset({Scalar.INT})
        case float():
            return frozenset({Scalar.FLOAT})
        case str():
            return frozenset({Scalar.STRING})
        case clingo.Symbol():
            return frozenset({Scalar.SYMBOL})
        case list() if not value:
            return frozenset({ListOf(UnknownType)})
        case list():
            return frozenset(ListOf(t) for item in value for t in _value_to_type(item))
        case tuple():
            return frozenset(
                TupleOf(tuple(element_types))
                for element_types in itertools.product(*(_value_to_type(item) for item in value))
            )
        case set() if not value:
            return frozenset({SetOf(UnknownType)})
        case set():
            return frozenset(SetOf(t) for item in value for t in _value_to_type(item))
        case dict() if not value:
            return frozenset({DictOf(UnknownType, UnknownType)})
        case dict():
            return frozenset(
                DictOf(key_type, value_type)
                for key, item_value in value.items()
                for key_type in _value_to_type(key)
                for value_type in _value_to_type(item_value)
            )
        case _:
            return frozenset({UnsupportedType})


def _globals_to_type_env(global_env: Mapping[str, object]) -> dict[str, frozenset[TypeInfo]]:
    return {name: _value_to_type(value) for name, value in global_env.items() if isinstance(name, str)}


class StatementAnalysisResult(NamedTuple):
    """Result of a statement-level name/type analysis."""

    name_types: dict[str, frozenset[TypeInfo]]
    unsupported_events: tuple[tuple[str | None, str], ...] = ()


class _StatementAnalyzer(ast.NodeVisitor):
    """Collect names and inferred types with conservative statement analysis."""

    _SUPPORTED_STATEMENTS = (
        ast.Assign,
        ast.AnnAssign,
        ast.If,
        ast.While,
        ast.For,
        ast.Pass,
        ast.Break,
        ast.Continue,
    )

    def __init__(
        self,
        source: str,
        global_value_env: Mapping[str, object] | None,
        local_type_env: dict[str, frozenset[TypeInfo]] | None,
    ) -> None:
        self.source = source
        self.name_types: dict[str, frozenset[TypeInfo]] = {}
        self.assigned_names: set[str] = set()
        self.unsupported_event_list: list[tuple[str | None, str]] = []
        self._global_values: dict[str, object] = {} if not global_value_env else dict(global_value_env)
        self._global_env: dict[str, frozenset[TypeInfo]] = (
            {} if not global_value_env else _globals_to_type_env(global_value_env)
        )
        self._env: dict[str, frozenset[TypeInfo]] = {} if not local_type_env else dict(local_type_env)

    def _resolve_global_value(self, node: ast.AST) -> object:
        match node:
            case ast.Name(id=name):
                if name in self._global_values:
                    return self._global_values[name]
                if hasattr(builtins, name):
                    return getattr(builtins, name)
                return _RUNTIME_MISSING
            case ast.Attribute(value=value, attr=attr):
                base_value = self._resolve_global_value(value)
                try:
                    assert base_value is not _RUNTIME_MISSING
                    return getattr(base_value, attr)
                except Exception:
                    return _RUNTIME_MISSING
            case _:
                return _RUNTIME_MISSING

    def _infer_global_reference_type(self, node: ast.AST) -> frozenset[TypeInfo]:
        runtime_value = self._resolve_global_value(node)
        if runtime_value is not _RUNTIME_MISSING:
            return _value_to_type(runtime_value)

        if isinstance(node, ast.Name):
            return self._global_env.get(node.id, frozenset({UnknownType}))

        return frozenset({UnknownType})

    def _mark_unsupported(self, node: ast.AST, reason: str) -> None:
        self.unsupported_event_list.append((ast.get_source_segment(self.source, node), reason))

    def _record_assignment_types(self, name: str, types: frozenset[TypeInfo]) -> None:
        self.assigned_names.add(name)
        self._env[name] = types

    def _visit_branch(
        self,
        statements: list[ast.stmt],
        entry_env: dict[str, frozenset[TypeInfo]],
    ) -> dict[str, frozenset[TypeInfo]]:
        self._env = entry_env.copy()
        for statement in statements:
            self.visit(statement)
        return self._env.copy()

    def _merge_envs(
        self,
        entry_env: dict[str, frozenset[TypeInfo]],
        *branch_envs: dict[str, frozenset[TypeInfo]],
    ) -> dict[str, frozenset[TypeInfo]]:
        merged = entry_env.copy()
        all_names = set().union(*(set(env) for env in branch_envs))
        for name in all_names:
            merged[name] = frozenset(
                inferred_type for env in branch_envs for inferred_type in env.get(name, frozenset({UnknownType}))
            )
        return merged

    def _infer_subscript_type(self, value: ast.AST, slice_node: ast.AST) -> frozenset[TypeInfo]:
        container_types = self._infer_expr_type(value)
        self._infer_expr_type(slice_node)
        out: set[TypeInfo] = set()
        index_value = slice_node.value if isinstance(slice_node, ast.Constant) else None

        for container_t in container_types:
            match container_t:
                case t if t is UnsupportedType or t is UnknownType:
                    out.add(t)
                case ListOf(element_types=element_type):
                    out.add(element_type)
                case TupleOf(element_types=element_types):
                    if isinstance(index_value, int) and 0 <= index_value < len(element_types):
                        out.add(element_types[index_value])
                    else:
                        out.update(element_types)
                case RepeatedTupleOf(element_type=element_type):
                    out.add(element_type)
                case DictOf(value_types=value_type):
                    out.add(value_type)
                case _:
                    out.add(UnknownType)

        return frozenset(out)

    def _infer_expr_type(self, node: ast.AST | None) -> frozenset[TypeInfo]:
        match node:
            case None:
                return frozenset({UnknownType})

            case ast.Constant(value=value):
                return _value_to_type(value)

            case ast.Name(id=name) as name_node:
                return self._env.get(name, self._infer_global_reference_type(name_node))

            case ast.Call() as call_node:
                if not isinstance(call_node.func, (ast.Name, ast.Attribute)):
                    self._mark_unsupported(call_node.func, "unsupported expression: callable form")
                    return frozenset({UnknownType})

                if any(isinstance(arg, ast.Starred) for arg in call_node.args) or any(
                    keyword.arg is None for keyword in call_node.keywords
                ):
                    self._mark_unsupported(call_node, "unsupported expression: positional/keyword unpacking")
                    return frozenset({UnknownType})

                inferred_func_types = frozenset(
                    inferred_type
                    for inferred_type in self._infer_expr_type(call_node.func)
                    if isinstance(inferred_type, FunctionType)
                )

                return get_return_types(
                    tuple(self._infer_expr_type(arg) for arg in call_node.args),
                    inferred_func_types,
                    static_overloads=resolve_static_overloads(
                        static_function_name=(
                            call_node.func.id
                            if isinstance(call_node.func, ast.Name) and not call_node.keywords
                            else None
                        ),
                    ),
                )

            case ast.keyword(arg=None):
                self._mark_unsupported(node, "unsupported expression: keyword unpacking")
                return frozenset({UnknownType})

            case ast.keyword(value=value):
                return self._infer_expr_type(value)

            case ast.BoolOp(values=values):
                return frozenset(
                    inferred_type for expression in values for inferred_type in self._infer_expr_type(expression)
                )

            case ast.Compare(left=left, comparators=comparators):
                return self._infer_compare_type(left, node.ops, comparators)

            case ast.IfExp(test=test, body=body, orelse=orelse):
                self._infer_expr_type(test)
                return self._infer_expr_type(body) | self._infer_expr_type(orelse)

            case ast.BinOp(left=left, op=op, right=right):
                return self._infer_operator_type(op, (self._infer_expr_type(left), self._infer_expr_type(right)))

            case ast.UnaryOp(op=op, operand=operand):
                return self._infer_operator_type(op, (self._infer_expr_type(operand),))

            case ast.Tuple(elts=elts):
                return frozenset(
                    TupleOf(tuple(element_types_choice))
                    for element_types_choice in itertools.product(*(self._infer_expr_type(element) for element in elts))
                )

            case ast.List(elts=elts) if not elts:
                return frozenset({ListOf(UnknownType)})

            case ast.List(elts=elts):
                return frozenset(
                    ListOf(element_type) for expression in elts for element_type in self._infer_expr_type(expression)
                )

            case ast.Set(elts=elts) if not elts:
                return frozenset({SetOf(UnknownType)})

            case ast.Set(elts=elts):
                return frozenset(
                    SetOf(element_type) for expression in elts for element_type in self._infer_expr_type(expression)
                )

            case ast.Dict(keys=keys, values=values) if not keys:
                return frozenset({DictOf(UnknownType, UnknownType)})

            case ast.Dict(keys=keys, values=values):
                return frozenset(
                    DictOf(key_type, value_type)
                    for key, value in zip(keys, values)
                    for key_type in self._infer_expr_type(key)
                    for value_type in self._infer_expr_type(value)
                )

            case ast.Subscript(value=value, slice=slice_node):
                return self._infer_subscript_type(value, slice_node)

            case ast.Attribute(value=value) as attribute_node:
                self._infer_expr_type(value)
                return self._infer_global_reference_type(attribute_node)

            case ast.expr():
                for child in ast.iter_child_nodes(node):
                    self._infer_expr_type(child)
                return frozenset({UnknownType})

            case _:
                self._mark_unsupported(node, f"unsupported expression: {type(node).__name__}")
                return frozenset({UnknownType})

    def _infer_operator_type(
        self,
        op: ast.operator | ast.unaryop,
        operand_type_sets: tuple[frozenset[TypeInfo], ...],
    ) -> frozenset[TypeInfo]:
        out: set[TypeInfo] = set()
        for operand_types in itertools.product(*operand_type_sets):
            resolved_types = get_return_types(
                tuple(frozenset({operand_type}) for operand_type in operand_types),
                frozenset(),
                static_overloads=resolve_static_overloads(operator=op),
            )
            if resolved_types:
                out.update(resolved_types)
        return frozenset(out)

    def _is_compare_pair_valid(self, op: ast.cmpop, left_t: TypeInfo, right_t: TypeInfo) -> bool:
        if isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
            return True

        if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            return (left_t == Scalar.STRING and right_t == Scalar.STRING) or (
                left_t in _ORDERABLE_SCALAR_TYPES and right_t in _ORDERABLE_SCALAR_TYPES
            )

        if isinstance(op, (ast.In, ast.NotIn)):
            return (right_t == Scalar.STRING and left_t == Scalar.STRING) or isinstance(
                right_t, (ListOf, TupleOf, RepeatedTupleOf, SetOf, DictOf)
            )

        return False

    def _infer_compare_type(
        self,
        left: ast.AST,
        ops: list[ast.cmpop],
        comparators: list[ast.expr],
    ) -> frozenset[TypeInfo]:
        result = frozenset({Scalar.BOOL})
        current_left_types = self._infer_expr_type(left)

        for op, comparator in zip(ops, comparators):
            right_types = self._infer_expr_type(comparator)

            link_has_unsupported = UnsupportedType in current_left_types or UnsupportedType in right_types
            link_has_unknown = UnknownType in current_left_types or UnknownType in right_types
            link_has_known_valid = any(
                left_t not in (UnknownType, UnsupportedType)
                and right_t not in (UnknownType, UnsupportedType)
                and self._is_compare_pair_valid(op, left_t, right_t)
                for left_t in current_left_types
                for right_t in right_types
            )

            if not (link_has_known_valid or link_has_unsupported or link_has_unknown):
                return frozenset()

            if not link_has_known_valid:
                result = result - frozenset({Scalar.BOOL})
            if link_has_unsupported:
                result = result | frozenset({UnsupportedType})
            if link_has_unknown:
                result = result | frozenset({UnknownType})

            current_left_types = right_types

        return result

    def _bind_target(self, target: ast.AST, value: ast.AST | None, value_types: frozenset[TypeInfo]) -> None:
        match target:
            case ast.Name(id=name):
                self._record_assignment_types(name, value_types)
                return

            case ast.Starred(value=starred_value):
                self._bind_target(starred_value, None, frozenset({ListOf(UnknownType)}))
                return

            case ast.Tuple(elts=elts) | ast.List(elts=elts):
                if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(elts):
                    for sub_target, sub_value in zip(elts, value.elts):
                        self._bind_target(sub_target, sub_value, self._infer_expr_type(sub_value))
                    return

                for sub_target in elts:
                    if isinstance(sub_target, ast.Starred):
                        self._bind_target(sub_target, None, frozenset({ListOf(UnknownType)}))
                    else:
                        self._bind_target(sub_target, None, frozenset({UnknownType}))
                return

            case _:
                self._mark_unsupported(target, f"unsupported assignment target: {type(target).__name__}")

    def generic_visit(self, node: ast.AST) -> None:
        self._mark_unsupported(node, f"unsupported statement: {type(node).__name__}")

    def visit_Module(self, node: ast.Module) -> None:
        for statement in node.body:
            if isinstance(statement, self._SUPPORTED_STATEMENTS):
                self.visit(statement)
            else:
                self._mark_unsupported(
                    statement,
                    f"unsupported statement: {type(statement).__name__}",
                )

    def visit_Assign(self, node: ast.Assign) -> None:
        value_types = self._infer_expr_type(node.value)
        for target in node.targets:
            self._bind_target(target, node.value, value_types)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._infer_expr_type(node.annotation)
        value_types = self._infer_expr_type(node.value)
        self._bind_target(node.target, node.value, value_types)

    def visit_If(self, node: ast.If) -> None:
        self._infer_expr_type(node.test)
        entry_env = self._env.copy()
        body_env = self._visit_branch(node.body, entry_env)
        else_env = self._visit_branch(node.orelse, entry_env)
        self._env = self._merge_envs(entry_env, body_env, else_env)

    def visit_While(self, node: ast.While) -> None:
        self._infer_expr_type(node.test)
        entry_env = self._env.copy()
        body_env = self._visit_branch(node.body, entry_env)
        else_env = self._visit_branch(node.orelse, entry_env)
        self._env = self._merge_envs(entry_env, body_env, else_env)

    def visit_For(self, node: ast.For) -> None:
        self._infer_expr_type(node.iter)
        self._bind_target(node.target, None, frozenset({UnknownType}))

        entry_env = self._env.copy()
        body_env = self._visit_branch(node.body, entry_env)
        else_env = self._visit_branch(node.orelse, entry_env)
        self._env = self._merge_envs(entry_env, body_env, else_env)


def analyze_python_statement_types(
    snippet: str,
    global_env: Mapping[str, object] | None = None,
    local_types: dict[str, frozenset[TypeInfo]] | None = None,
) -> StatementAnalysisResult:
    """Return possible types for names introduced by a simple Python snippet.

    The analysis is conservative:
    - supported expressions contribute inferred or unknown local types
    - unsupported constructs are flagged but do not invalidate unrelated results
    """

    try:
        tree = ast.parse(snippet, mode="exec")
    except SyntaxError as exc:
        witness = exc.text.strip() if exc.text else None
        return StatementAnalysisResult(
            name_types={},
            unsupported_events=((witness, "syntax error"),),
        )

    analyzer = _StatementAnalyzer(snippet, global_env, local_types)
    analyzer.visit(tree)
    exit_name_types = {name: analyzer._env.get(name, frozenset({UnknownType})) for name in analyzer.assigned_names}
    return StatementAnalysisResult(
        name_types=exit_name_types,
        unsupported_events=tuple(analyzer.unsupported_event_list),
    )
