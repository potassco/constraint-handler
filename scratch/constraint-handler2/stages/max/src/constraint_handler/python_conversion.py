"""Lower internal expressions to closed Python callable source."""

import ast

from .internal_input import (
    Expr,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    VariableRef,
)
from .python_input import Operator


class _Substitute(ast.NodeTransformer):
    """Insert expression trees into fixed operator templates."""

    def __init__(self, arguments: list[ast.expr]) -> None:
        """Bind positional template names to converted arguments."""
        self.arguments = {f"_arg{index}": arg for index, arg in enumerate(arguments)}

    def visit_Name(self, node: ast.Name) -> ast.expr:
        """Replace template arguments without traversing inserted expressions."""
        return self.arguments.get(node.id, node)


_TEMPLATES: dict[Operator, str] = {
    Operator.eq: "(lambda _key: _key(_arg0) == _key(_arg1))(__import__('constraint_handler.domains.values', fromlist=('value_key',)).value_key)",
    Operator.neq: "(lambda _key: _key(_arg0) != _key(_arg1))(__import__('constraint_handler.domains.values', fromlist=('value_key',)).value_key)",
    Operator.concat: "_arg0 + _arg1",
    Operator.length: "len(_arg0)",
    Operator.cardinality: "len(_arg0)",
    Operator.get_or_else: "(lambda _fallback: _fallback if _fallback is not None else _arg1)(_arg0)",
    Operator.if_: "_arg1 if _arg0 is True else None",
    Operator.ite: "_arg1 if _arg0 is True else _arg2",
    Operator.has_value: "_arg0 is not None",
    Operator.abs: "abs(_arg0)",
    Operator.minus: "-_arg0",
    Operator.mod: "_arg0 % _arg1",
    Operator.sub: "_arg0 - _arg1",
    Operator.int_div: "int(_arg0 // _arg1)",
    Operator.real_div: "_arg0 / _arg1",
    Operator.pow: "_arg0 ** _arg1",
    Operator.leq: "_arg0 <= _arg1",
    Operator.lt: "_arg0 < _arg1",
    Operator.geq: "_arg0 >= _arg1",
    Operator.gt: "_arg0 > _arg1",
    Operator.real_from_int: "float(_arg0)",
    Operator.int_from_real: "int(_arg0)",
    Operator.lnot: "not _arg0",
    Operator.snot: "_arg0 is False",
    Operator.wnot: "_arg0 is not True",
    Operator.limp: "not _arg0 or _arg1",
    Operator.set_isin: "_arg0 in _arg1",
    Operator.set_notin: "_arg0 not in _arg1",
    Operator.union: "_arg0 | _arg1",
    Operator.inter: "_arg0 & _arg1",
    Operator.diff: "_arg0 - _arg1",
    Operator.subset: "_arg0 <= _arg1",
    Operator.tuple_get: "_arg0[_arg1] if _arg1 >= 0 else ()[0]",
    Operator.set_fold: "__import__('functools').reduce(_arg0, sorted(_arg1, key=repr), _arg2)",
}


class _Converter:
    """Generate lexical bindings independent of caller variable names."""

    def __init__(self) -> None:
        """Start a deterministic sequence of Python-safe parameter names."""
        self.counter = 0

    def callable(
        self,
        parameters: tuple[VariableRef, ...],
        body: Expr,
        bindings: dict[VariableRef, str],
    ) -> ast.Lambda:
        """Convert a lambda while retaining captured outer bindings."""
        local = dict(bindings)
        names: list[str] = []
        for parameter in parameters:
            name = f"_value{self.counter}"
            self.counter += 1
            names.append(name)
            local[parameter] = name
        return ast.Lambda(
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg=name) for name in names],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=self.expression(body, local),
        )

    def expression(
        self, expr: OperationArg, bindings: dict[VariableRef, str]
    ) -> ast.expr:
        """Translate expressions and descriptors without evaluating user code."""
        match expr:
            case ValueDef(_, value):
                return ast.Constant(value=value)
            case VariableRef():
                return ast.Name(id=bindings[expr], ctx=ast.Load())
            case Lambda(parameters, body):
                return self.callable(parameters, body, bindings)
            case Python(source):
                return ast.Call(
                    func=ast.Name(id="eval", ctx=ast.Load()),
                    args=[
                        ast.Constant(value=source),
                        ast.Dict(
                            keys=[ast.Constant(value="math")],
                            values=[ast.Name(id="math", ctx=ast.Load())],
                        ),
                    ],
                    keywords=[],
                )
            case tuple():
                return ast.Tuple(
                    elts=[self.expression(item, bindings) for item in expr],
                    ctx=ast.Load(),
                )
            case frozenset():
                items = [
                    self.expression(item, bindings) for item in sorted(expr, key=repr)
                ]
                return ast.Call(
                    func=ast.Name(id="frozenset", ctx=ast.Load()),
                    args=[ast.Tuple(elts=items, ctx=ast.Load())],
                    keywords=[],
                )
            case Operation(op, arguments):
                args = [self.expression(arg, bindings) for arg in arguments]
                if op == Operator.make_tuple:
                    return ast.Tuple(elts=args, ctx=ast.Load())
                if op in {Operator.python_eval, Operator.lambda_}:
                    return ast.Call(func=args[0], args=args[1:], keywords=[])
                if op in {Operator.linear_integer, Operator.linear_comparison}:
                    if op == Operator.linear_comparison:
                        args = args[1:]
                    terms: list[ast.expr] = [
                        ast.BinOp(left=pair.elts[0], op=ast.Mult(), right=pair.elts[1])
                        for pair in args[:-1]
                        if isinstance(pair, ast.Tuple)
                    ]
                    terms.append(args[-1])
                    total = ast.Call(
                        func=ast.Name(id="sum", ctx=ast.Load()),
                        args=[ast.Tuple(elts=terms, ctx=ast.Load())],
                        keywords=[],
                    )
                    if op == Operator.linear_integer:
                        return total
                    relation = arguments[0]
                    assert isinstance(relation, ValueDef)
                    comparison = {
                        "eq": ast.Eq,
                        "neq": ast.NotEq,
                        "lt": ast.Lt,
                        "leq": ast.LtE,
                        "gt": ast.Gt,
                        "geq": ast.GtE,
                    }[str(relation.value)]
                    return ast.Compare(
                        left=total,
                        ops=[comparison()],
                        comparators=[ast.Constant(value=0)],
                    )
                if op in {Operator.add, Operator.mult}:
                    result: ast.expr = ast.Constant(
                        value=0 if op == Operator.add else 1
                    )
                    for arg in args:
                        result = ast.BinOp(
                            left=result,
                            op=ast.Add() if op == Operator.add else ast.Mult(),
                            right=arg,
                        )
                    return result
                if op in {
                    Operator.conj,
                    Operator.disj,
                    Operator.max,
                    Operator.min,
                    Operator.set_make,
                }:
                    name = {
                        Operator.conj: "all",
                        Operator.disj: "any",
                        Operator.max: "max",
                        Operator.min: "min",
                        Operator.set_make: "frozenset",
                    }[op]
                    return ast.Call(
                        func=ast.Name(id=name, ctx=ast.Load()),
                        args=[ast.Tuple(elts=args, ctx=ast.Load())],
                        keywords=[],
                    )
                if op in {Operator.lxor, Operator.leqv}:
                    comparisons: list[ast.expr] = [
                        ast.Compare(
                            left=arg,
                            ops=[ast.Is()],
                            comparators=[ast.Constant(value=op == Operator.lxor)],
                        )
                        for arg in args
                    ]
                    count = ast.Call(
                        func=ast.Name(id="sum", ctx=ast.Load()),
                        args=[ast.Tuple(elts=comparisons, ctx=ast.Load())],
                        keywords=[],
                    )
                    return ast.Compare(
                        left=ast.BinOp(
                            left=count, op=ast.Mod(), right=ast.Constant(value=2)
                        ),
                        ops=[ast.Eq()],
                        comparators=[
                            ast.Constant(value=1 if op == Operator.lxor else 0)
                        ],
                    )
                if op in {
                    Operator.sqrt,
                    Operator.cos,
                    Operator.sin,
                    Operator.tan,
                    Operator.acos,
                    Operator.asin,
                    Operator.atan,
                    Operator.floor,
                    Operator.ceil,
                }:
                    template = f"math.{op.value}(_arg0)"
                else:
                    template = _TEMPLATES[op]
                return _Substitute(args).visit(ast.parse(template, mode="eval").body)


def convert(parameters: tuple[VariableRef, ...], body: Expr) -> Python:
    """Compile a closed expression over explicit inputs into a Python descriptor."""
    tree = ast.fix_missing_locations(_Converter().callable(parameters, body, {}))
    return Python(ast.unparse(tree))
