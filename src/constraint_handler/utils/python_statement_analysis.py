"""Analyze simple Python snippets and infer variable type sets."""

from __future__ import annotations

import ast
from collections import namedtuple
from dataclasses import dataclass


class UnknownType:
    """Marker type used when expression type cannot be inferred."""


ListOf = namedtuple("ListOf", ["element_types"])
TupleOf = namedtuple("TupleOf", ["element_types"])
SetOf = namedtuple("SetOf", ["element_types"])
DictOf = namedtuple("DictOf", ["key_types", "value_types"])
ScalarType = namedtuple("ScalarType", ["typ"])

TypeInfo = ScalarType | ListOf | TupleOf | SetOf | DictOf | type[UnknownType]
_NONE_SCALAR = ScalarType(type(None))
_BOOL_SCALAR = ScalarType(bool)
_INT_SCALAR = ScalarType(int)
_FLOAT_SCALAR = ScalarType(float)
_STR_SCALAR = ScalarType(str)

_UNKNOWN_TYPES = frozenset({UnknownType})
_NONE_TYPES = frozenset({_NONE_SCALAR})
_BOOL_TYPES = frozenset({_BOOL_SCALAR})
_INT_TYPES = frozenset({_INT_SCALAR})
_FLOAT_TYPES = frozenset({_FLOAT_SCALAR})
_STR_TYPES = frozenset({_STR_SCALAR})
_NUMERIC_SCALAR_TYPES = frozenset({_INT_SCALAR, _FLOAT_SCALAR})
_ORDERABLE_SCALAR_TYPES = frozenset({_BOOL_SCALAR, _INT_SCALAR, _FLOAT_SCALAR})
_UNKNOWN_LIST_TYPE = ListOf(_UNKNOWN_TYPES)
_UNKNOWN_LIST_TYPES = frozenset({_UNKNOWN_LIST_TYPE})
_CONTAINER_TYPE_CLASSES = (ListOf, TupleOf, SetOf, DictOf)
_CONSTANT_TYPE_SETS = (
    (type(None), _NONE_TYPES),
    (bool, _BOOL_TYPES),
    (int, _INT_TYPES),
    (float, _FLOAT_TYPES),
    (str, _STR_TYPES),
)


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

    def __init__(self, source: str) -> None:
        self.source = source
        self.name_types: dict[str, frozenset[TypeInfo]] = {}
        self.unsupported_witness: str | None = None
        self.unsupported_reason: str | None = None
        self._env: dict[str, frozenset[TypeInfo]] = {}

    def _mark_unsupported(self, node: ast.AST, reason: str) -> None:
        if self.unsupported_witness is None:
            self.unsupported_witness = ast.get_source_segment(self.source, node)
            self.unsupported_reason = reason

    def _record_assignment_types(self, name: str, types: frozenset[TypeInfo]) -> None:
        self.name_types[name] = self.name_types.get(name, frozenset()) | types
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
                set().union(*(set(env.get(name, _UNKNOWN_TYPES)) for env in branch_envs))
            )
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
                        for position_types in element_types:
                            out.update(position_types)
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
                for py_type, inferred_types in _CONSTANT_TYPE_SETS:
                    if isinstance(value, py_type):
                        return inferred_types
                return _UNKNOWN_TYPES

            case ast.Name(id=name):
                return self._env.get(name, _UNKNOWN_TYPES)

            case ast.Call() as call_node:
                self._scan_call(call_node)
                return _UNKNOWN_TYPES

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

            case ast.UnaryOp(op=ast.Not(), operand=operand):
                inferred = self._infer_expr_type(operand)
                if UnknownType in inferred:
                    if any(t is not UnknownType for t in inferred):
                        return frozenset({_BOOL_SCALAR, UnknownType})
                    return _UNKNOWN_TYPES
                if inferred:
                    return _BOOL_TYPES
                return frozenset()

            case ast.UnaryOp(op=ast.UAdd() | ast.USub(), operand=operand):
                inferred = self._infer_expr_type(operand)
                return inferred & (_NUMERIC_SCALAR_TYPES | {UnknownType})

            case ast.UnaryOp(op=ast.Invert(), operand=operand):
                inferred = self._infer_expr_type(operand)
                if _INT_SCALAR in inferred or _BOOL_SCALAR in inferred:
                    if UnknownType in inferred:
                        return frozenset({_INT_SCALAR, UnknownType})
                    return _INT_TYPES
                if UnknownType in inferred:
                    return _UNKNOWN_TYPES
                return frozenset()

            case ast.Tuple(elts=elts):
                element_types = tuple(self._infer_expr_type(element) for element in elts)
                return frozenset({TupleOf(element_types)})

            case ast.List(elts=elts):
                return frozenset({ListOf(self._union_inferred_types(elts))})

            case ast.Set(elts=elts):
                return frozenset({SetOf(self._union_inferred_types(elts))})

            case ast.Dict(keys=keys, values=values):
                return frozenset({
                    DictOf(
                        self._union_inferred_types(keys),
                        self._union_inferred_types(values),
                    )
                })

            case ast.Subscript(value=value, slice=slice_node):
                return self._infer_subscript_type(value, slice_node)

            case ast.Attribute(value=value):
                self._infer_expr_type(value)
                return _UNKNOWN_TYPES

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
        numeric_to_numeric_ops = (ast.Add, ast.Sub, ast.Mult, ast.Mod, ast.Pow)
        int_to_int_ops = (ast.FloorDiv, ast.LShift, ast.RShift, ast.BitAnd, ast.BitOr, ast.BitXor)
        for left_t in left:
            for right_t in right:
                if UnknownType in (left_t, right_t):
                    out.add(UnknownType)
                elif isinstance(op, ast.Add) and left_t == _STR_SCALAR and right_t == _STR_SCALAR:
                    out.add(_STR_SCALAR)
                elif isinstance(op, ast.Add) and isinstance(left_t, ListOf) and isinstance(right_t, ListOf):
                    out.add(ListOf(left_t.element_types | right_t.element_types))
                elif left_t in _NUMERIC_SCALAR_TYPES and right_t in _NUMERIC_SCALAR_TYPES:
                    if isinstance(op, numeric_to_numeric_ops):
                        if _FLOAT_SCALAR in {left_t, right_t}:
                            out.add(_FLOAT_SCALAR)
                        else:
                            out.add(_INT_SCALAR)
                    elif isinstance(op, ast.Div):
                        out.add(_FLOAT_SCALAR)
                    elif isinstance(op, int_to_int_ops) and left_t == _INT_SCALAR and right_t == _INT_SCALAR:
                        out.add(_INT_SCALAR)
        return frozenset(out)

    def _is_compare_pair_valid(self, op: ast.cmpop, left_t: TypeInfo, right_t: TypeInfo) -> bool:
        if isinstance(op, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
            return True

        if isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
            return (left_t == _STR_SCALAR and right_t == _STR_SCALAR) or (
                left_t in _ORDERABLE_SCALAR_TYPES and right_t in _ORDERABLE_SCALAR_TYPES
            )

        if isinstance(op, (ast.In, ast.NotIn)):
            return (right_t == _STR_SCALAR and left_t == _STR_SCALAR) or isinstance(
                right_t, _CONTAINER_TYPE_CLASSES
            )

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

            link_result = (
                (_BOOL_TYPES if link_has_known_valid else frozenset())
                | (_UNKNOWN_TYPES if link_has_unknown else frozenset())
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


def analyze_python_statement_types(snippet: str) -> StatementAnalysisResult:
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

    analyzer = _StatementAnalyzer(snippet)
    analyzer.visit(tree)
    return StatementAnalysisResult(
        name_types=analyzer.name_types,
        has_unsupported_features=analyzer.unsupported_witness is not None,
        unsupported_witness=analyzer.unsupported_witness,
        unsupported_reason=analyzer.unsupported_reason,
    )
