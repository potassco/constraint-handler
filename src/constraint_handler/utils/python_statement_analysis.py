"""Analyze simple Python snippets and infer variable type sets."""

from __future__ import annotations

import ast
import builtins
import collections.abc as collections_abc
import inspect
import types
import typing
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from constraint_handler.utils.python_type_model import (
    DictOf,
    FunctionType,
    ListOf,
    RepeatedTupleOf,
    SetOf,
    TupleOf,
    TypeInfo,
    UnknownType,
    _BOOL_SCALAR,
    _FLOAT_SCALAR,
    _INT_SCALAR,
    _NONE_SCALAR,
    _STR_SCALAR,
)
from constraint_handler.utils.python_type_signatures import (
    BINARY_OPERATOR_OVERLOADS,
    MATH_FUNCTION_TYPES,
    UNARY_OPERATOR_OVERLOADS,
)

_RUNTIME_MISSING = object()
_UNKNOWN_TYPES = frozenset({UnknownType})
_UNKNOWN_FUNCTION_TYPE = FunctionType(None, _UNKNOWN_TYPES)
_UNKNOWN_LIST_TYPE = ListOf(_UNKNOWN_TYPES)
_BOOL_TYPES = frozenset({_BOOL_SCALAR})
_ORDERABLE_SCALAR_TYPES = frozenset({_BOOL_SCALAR, _INT_SCALAR, _FLOAT_SCALAR})
_UNKNOWN_LIST_TYPES = frozenset({_UNKNOWN_LIST_TYPE})
_CONTAINER_TYPE_CLASSES = (ListOf, TupleOf, RepeatedTupleOf, SetOf, DictOf)


def _callable_annotation_to_function_type(annotation_args: tuple[object, ...]) -> FunctionType:
    if len(annotation_args) != 2:
        return _UNKNOWN_FUNCTION_TYPE

    input_part, return_part = annotation_args
    return_types = _annotation_to_types(return_part)

    match input_part:
        case _ if input_part is Ellipsis:
            return FunctionType(None, return_types)
        case [*param_annotations] | (*param_annotations,):
            input_types = tuple(_annotation_to_types(param_ann) for param_ann in param_annotations)
            return FunctionType(input_types, return_types)
        case _:
            return _UNKNOWN_FUNCTION_TYPE


def _matches_function_inputs(function_type: FunctionType, arg_types: tuple[TypeInfo, ...]) -> bool:
    return function_type.input_types is None or (
        len(function_type.input_types) == len(arg_types)
        and all(arg_type in accepted_types for arg_type, accepted_types in zip(arg_types, function_type.input_types))
    )


def _annotation_to_types(annotation: object) -> frozenset[TypeInfo]:
    origin = typing.get_origin(annotation)
    if origin in (types.UnionType, typing.Union):
        return frozenset().union(*(_annotation_to_types(arg) for arg in typing.get_args(annotation)))
    return frozenset({_annotation_to_type(annotation)})


def _annotation_to_type(annotation: object) -> TypeInfo:
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    dispatch = annotation if origin is None else origin

    match dispatch:
        case inspect.Signature.empty | typing.Any | builtins.object:
            return UnknownType
        case types.NoneType:
            return _NONE_SCALAR
        case builtins.bool:
            return _BOOL_SCALAR
        case builtins.int:
            return _INT_SCALAR
        case builtins.float:
            return _FLOAT_SCALAR
        case builtins.str:
            return _STR_SCALAR
        case builtins.list:
            element_types = _UNKNOWN_TYPES if not args else _annotation_to_types(args[0])
            return ListOf(element_types)
        case builtins.set:
            element_types = _UNKNOWN_TYPES if not args else _annotation_to_types(args[0])
            return SetOf(element_types)
        case builtins.dict:
            if len(args) == 2:
                return DictOf(_annotation_to_types(args[0]), _annotation_to_types(args[1]))
            return DictOf(_UNKNOWN_TYPES, _UNKNOWN_TYPES)
        case builtins.tuple:
            if args.count(Ellipsis) == 1 and args[-1] is Ellipsis:
                pattern_types = tuple(_annotation_to_types(arg) for arg in args[:-1])
                if not pattern_types:
                    return UnknownType
                return RepeatedTupleOf(pattern_types)
            if Ellipsis in args:
                return UnknownType
            return TupleOf(tuple(_annotation_to_types(arg) for arg in args))
        case collections_abc.Callable:
            return _callable_annotation_to_function_type(args)
        case _:
            return UnknownType


def _callable_type_info(func: collections_abc.Callable) -> FunctionType:
    input_types: tuple[frozenset[TypeInfo], ...] | None = None
    return_types = _UNKNOWN_TYPES

    try:
        hints = typing.get_type_hints(func)
    except Exception:
        hints = {}

    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        signature = None

    if signature is not None:
        inferred_inputs: list[frozenset[TypeInfo]] = []
        saw_var_args = False
        for parameter in signature.parameters.values():
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                saw_var_args = True
                break
            if parameter.name in hints:
                inferred_inputs.append(_annotation_to_types(hints[parameter.name]))
            elif parameter.annotation is not inspect.Signature.empty:
                inferred_inputs.append(_annotation_to_types(parameter.annotation))
            else:
                inferred_inputs.append(_UNKNOWN_TYPES)
        if not saw_var_args:
            input_types = tuple(inferred_inputs)

    if "return" in hints:
        return_types = _annotation_to_types(hints["return"])
    elif signature is not None and signature.return_annotation is not inspect.Signature.empty:
        return_types = _annotation_to_types(signature.return_annotation)

    module_name = getattr(func, "__module__", None)
    function_name = getattr(func, "__name__", None)
    if module_name == "math" and isinstance(function_name, str):
        math_type = MATH_FUNCTION_TYPES.get(function_name)
        if math_type is not None:
            if input_types is None or all(param_types == _UNKNOWN_TYPES for param_types in input_types):
                input_types = math_type.input_types
            if return_types == _UNKNOWN_TYPES:
                return_types = math_type.return_types

    return FunctionType(input_types, return_types)


def _union_value_types(values: Iterable[object]) -> frozenset[TypeInfo]:
    return frozenset(_value_to_type(value) for value in values)


def _value_to_type(value: object) -> TypeInfo:
    match value:
        case _ if callable(value):
            return _callable_type_info(value)
        case None:
            return _NONE_SCALAR
        case bool():
            return _BOOL_SCALAR
        case int():
            return _INT_SCALAR
        case float():
            return _FLOAT_SCALAR
        case str():
            return _STR_SCALAR
        case list() as values if not values:
            return _UNKNOWN_LIST_TYPE
        case list() as values:
            return ListOf(_union_value_types(values))
        case tuple() as values:
            return TupleOf(tuple(frozenset({_value_to_type(item)}) for item in values))
        case set() as values if not values:
            return SetOf(_UNKNOWN_TYPES)
        case set() as values:
            return SetOf(_union_value_types(values))
        case dict() as values if not values:
            return DictOf(_UNKNOWN_TYPES, _UNKNOWN_TYPES)
        case dict() as values:
            return DictOf(_union_value_types(values.keys()), _union_value_types(values.values()))
        case _:
            return UnknownType


def _globals_to_type_env(global_env: Mapping[str, object]) -> dict[str, frozenset[TypeInfo]]:
    return {name: frozenset({_value_to_type(value)}) for name, value in global_env.items() if isinstance(name, str)}


@dataclass(frozen=True)
class StatementAnalysisResult:
    """Result of a statement-level name/type analysis."""

    name_types: dict[str, frozenset[TypeInfo]]
    has_unsupported_features: bool
    unsupported_witness: str | None = None
    unsupported_reason: str | None = None


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
        self.unsupported_witness: str | None = None
        self.unsupported_reason: str | None = None
        self._global_values: dict[str, object] = {} if not global_value_env else dict(global_value_env)
        self._global_env: dict[str, frozenset[TypeInfo]] = {} if not global_value_env else _globals_to_type_env(global_value_env)
        self._env: dict[str, frozenset[TypeInfo]] = {} if not local_type_env else dict(local_type_env)

    def _resolve_global_value(self, node: ast.AST) -> object:
        match node:
            case ast.Name(id=name):
                return self._global_values.get(name, _RUNTIME_MISSING)
            case ast.Attribute(value=value, attr=attr):
                base_value = self._resolve_global_value(value)
                if base_value is _RUNTIME_MISSING:
                    return _RUNTIME_MISSING
                try:
                    return getattr(base_value, attr)
                except Exception:
                    return _RUNTIME_MISSING
            case _:
                return _RUNTIME_MISSING

    def _infer_global_reference_type(self, node: ast.AST) -> frozenset[TypeInfo]:
        runtime_value = self._resolve_global_value(node)
        if runtime_value is not _RUNTIME_MISSING:
            return frozenset({_value_to_type(runtime_value)})

        if isinstance(node, ast.Name):
            return self._global_env.get(node.id, _UNKNOWN_TYPES)

        return _UNKNOWN_TYPES

    def _mark_unsupported(self, node: ast.AST, reason: str) -> None:
        if self.unsupported_witness is None:
            self.unsupported_witness = ast.get_source_segment(self.source, node)
            self.unsupported_reason = reason

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
            merged[name] = frozenset(set().union(*(set(env.get(name, _UNKNOWN_TYPES)) for env in branch_envs)))
        return merged

    def _union_inferred_types(self, expressions: list[ast.AST | None]) -> frozenset[TypeInfo]:
        return frozenset(set().union(*(self._infer_expr_type(expression) for expression in expressions)))

    def _infer_subscript_type(self, value: ast.AST, slice_node: ast.AST) -> frozenset[TypeInfo]:
        container_types = self._infer_expr_type(value)
        self._infer_expr_type(slice_node)
        out: set[TypeInfo] = set()
        index_value = slice_node.value if isinstance(slice_node, ast.Constant) else None

        for container_t in container_types:
            match container_t:
                case t if t is UnknownType:
                    out.add(UnknownType)
                case ListOf(element_types=element_types):
                    out.update(element_types)
                case TupleOf(element_types=element_types):
                    if isinstance(index_value, int) and 0 <= index_value < len(element_types):
                        out.update(element_types[index_value])
                    else:
                        out.update(*element_types)
                case RepeatedTupleOf(pattern_types=pattern_types):
                    if isinstance(index_value, int) and index_value >= 0 and pattern_types:
                        if index_value < len(pattern_types):
                            out.update(pattern_types[index_value])
                        else:
                            out.update(pattern_types[-1])
                    else:
                        out.update(*pattern_types)
                case DictOf(value_types=value_types):
                    out.update(value_types)
                case _:
                    out.add(UnknownType)

        return frozenset(out)

    def _infer_expr_type(self, node: ast.AST | None) -> frozenset[TypeInfo]:
        match node:
            case None:
                return _UNKNOWN_TYPES

            case ast.Constant(value=value):
                return frozenset({_value_to_type(value)})

            case ast.Name(id=name) as name_node:
                return self._env.get(name, self._infer_global_reference_type(name_node))

            case ast.Call() as call_node:
                self._scan_call(call_node)
                inferred_func_types = self._infer_expr_type(call_node.func)
                inferred_return_types: set[TypeInfo] = set()
                for func_type in inferred_func_types:
                    match func_type:
                        case FunctionType(input_types=_, return_types=return_types):
                            inferred_return_types.update(return_types)
                        case t if t is UnknownType:
                            inferred_return_types.add(UnknownType)
                        case _:
                            pass
                if not inferred_return_types:
                    return _UNKNOWN_TYPES
                return frozenset(inferred_return_types)

            case ast.keyword(arg=None):
                self._mark_unsupported(node, "unsupported expression: keyword unpacking")
                return _UNKNOWN_TYPES

            case ast.keyword(value=value):
                return self._infer_expr_type(value)

            case ast.BoolOp(values=values):
                return self._union_inferred_types(values)

            case ast.Compare(left=left, comparators=comparators):
                return self._infer_compare_type(left, node.ops, comparators)

            case ast.IfExp(test=test, body=body, orelse=orelse):
                self._infer_expr_type(test)
                return self._infer_expr_type(body) | self._infer_expr_type(orelse)

            case ast.BinOp(left=left, op=op, right=right):
                return self._infer_binop_type(op, self._infer_expr_type(left), self._infer_expr_type(right))

            case ast.UnaryOp(op=op, operand=operand):
                return self._infer_unaryop_type(op, self._infer_expr_type(operand))

            case ast.Tuple(elts=elts):
                element_types = tuple(self._infer_expr_type(element) for element in elts)
                return frozenset({TupleOf(element_types)})

            case ast.List(elts=elts):
                return frozenset({ListOf(self._union_inferred_types(elts))})

            case ast.Set(elts=elts):
                return frozenset({SetOf(self._union_inferred_types(elts))})

            case ast.Dict(keys=keys, values=values):
                return frozenset(
                    {
                        DictOf(
                            self._union_inferred_types(keys),
                            self._union_inferred_types(values),
                        )
                    }
                )

            case ast.Subscript(value=value, slice=slice_node):
                return self._infer_subscript_type(value, slice_node)

            case ast.Attribute(value=value) as attribute_node:
                self._infer_expr_type(value)
                return self._infer_global_reference_type(attribute_node)

            case ast.expr():
                for child in ast.iter_child_nodes(node):
                    self._infer_expr_type(child)
                return _UNKNOWN_TYPES

            case _:
                self._mark_unsupported(node, f"unsupported expression: {type(node).__name__}")
                return _UNKNOWN_TYPES

    def _infer_binop_type(
        self,
        op: ast.operator,
        left: frozenset[TypeInfo],
        right: frozenset[TypeInfo],
    ) -> frozenset[TypeInfo]:
        out: set[TypeInfo] = set()
        overloads = BINARY_OPERATOR_OVERLOADS.get(type(op), ())
        for left_t in left:
            for right_t in right:
                if UnknownType in (left_t, right_t):
                    out.add(UnknownType)
                    continue

                if isinstance(op, ast.Add) and isinstance(left_t, ListOf) and isinstance(right_t, ListOf):
                    out.add(ListOf(left_t.element_types | right_t.element_types))
                    continue

                out.update(*(overload.return_types for overload in overloads if _matches_function_inputs(overload, (left_t, right_t))))
        return frozenset(out)

    def _infer_unaryop_type(self, op: ast.unaryop, operand_types: frozenset[TypeInfo]) -> frozenset[TypeInfo]:
        out: set[TypeInfo] = set()
        overloads = UNARY_OPERATOR_OVERLOADS.get(type(op), ())
        for operand_type in operand_types:
            if operand_type is UnknownType:
                out.add(UnknownType)
                continue
            out.update(*(overload.return_types for overload in overloads if _matches_function_inputs(overload, (operand_type,))))
        return frozenset(out)

    def _is_compare_pair_valid(self, op: ast.cmpop, left_t: TypeInfo, right_t: TypeInfo) -> bool:
        if isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
            return True

        if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            return (left_t == _STR_SCALAR and right_t == _STR_SCALAR) or (
                left_t in _ORDERABLE_SCALAR_TYPES and right_t in _ORDERABLE_SCALAR_TYPES
            )

        if isinstance(op, (ast.In, ast.NotIn)):
            return (right_t == _STR_SCALAR and left_t == _STR_SCALAR) or isinstance(right_t, _CONTAINER_TYPE_CLASSES)

        return False

    def _infer_compare_type(
        self,
        left: ast.AST,
        ops: list[ast.cmpop],
        comparators: list[ast.expr],
    ) -> frozenset[TypeInfo]:
        result = _BOOL_TYPES
        current_left_types = self._infer_expr_type(left)

        for op, comparator in zip(ops, comparators):
            right_types = self._infer_expr_type(comparator)

            link_has_unknown = UnknownType in current_left_types or UnknownType in right_types
            link_has_known_valid = any(
                left_t is not UnknownType
                and right_t is not UnknownType
                and self._is_compare_pair_valid(op, left_t, right_t)
                for left_t in current_left_types
                for right_t in right_types
            )

            link_result = (_BOOL_TYPES if link_has_known_valid else frozenset()) | (
                _UNKNOWN_TYPES if link_has_unknown else frozenset()
            )
            if not link_result:
                return frozenset()

            if _BOOL_SCALAR not in link_result:
                result = result - _BOOL_TYPES
            if UnknownType in link_result:
                result = result | _UNKNOWN_TYPES

            current_left_types = right_types

        return result

    def _scan_call(self, node: ast.Call) -> None:
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            self._mark_unsupported(node.func, "unsupported expression: callable form")
        self._infer_expr_type(node.func)

        for arg in node.args:
            if isinstance(arg, ast.Starred):
                self._mark_unsupported(arg, "unsupported expression: positional unpacking")
            self._infer_expr_type(arg)

        for keyword in node.keywords:
            self._infer_expr_type(keyword)

    def _bind_target(self, target: ast.AST, value: ast.AST | None, value_types: frozenset[TypeInfo]) -> None:
        match target:
            case ast.Name(id=name):
                self._record_assignment_types(name, value_types)
                return

            case ast.Starred(value=starred_value):
                self._bind_target(starred_value, None, _UNKNOWN_LIST_TYPES)
                return

            case ast.Tuple(elts=elts) | ast.List(elts=elts):
                if isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == len(elts):
                    for sub_target, sub_value in zip(elts, value.elts):
                        self._bind_target(sub_target, sub_value, self._infer_expr_type(sub_value))
                    return

                for sub_target in elts:
                    if isinstance(sub_target, ast.Starred):
                        self._bind_target(sub_target, None, _UNKNOWN_LIST_TYPES)
                    else:
                        self._bind_target(sub_target, None, _UNKNOWN_TYPES)
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
        self._bind_target(node.target, None, _UNKNOWN_TYPES)

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
            has_unsupported_features=True,
            unsupported_witness=witness,
            unsupported_reason="syntax error",
        )

    analyzer = _StatementAnalyzer(snippet, global_env, local_types)
    analyzer.visit(tree)
    exit_name_types = {
        name: analyzer._env.get(name, _UNKNOWN_TYPES)
        for name in analyzer.assigned_names
    }
    return StatementAnalysisResult(
        name_types=exit_name_types,
        has_unsupported_features=analyzer.unsupported_witness is not None,
        unsupported_witness=analyzer.unsupported_witness,
        unsupported_reason=analyzer.unsupported_reason,
    )
