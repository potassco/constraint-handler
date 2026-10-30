"""Convert old constraint-handler ASP fact files into the new ConstraintStore."""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from constraint_handler import (
    LABEL_ANONYMOUS,
    ConstraintStore,
    Expr,
    FailIntegrityExn,
    Lambda,
    Operation,
    OperationArg,
    Operator,
    Python,
    VariableRef,
)
from constraint_handler.internal_input import SetVariable, Variable


class ConversionError(ValueError):
    """Raise when old input facts are syntactically invalid or malformed."""


class UnsupportedFeatureError(ConversionError):
    """Raise when an old language feature is not supported by the new ConstraintStore."""


@dataclass(frozen=True, slots=True)
class NumberTerm:
    """Represent an integer literal term in ASP."""

    value: int


@dataclass(frozen=True, slots=True)
class StringTerm:
    """Represent a double-quoted string literal term in ASP."""

    value: str


@dataclass(frozen=True, slots=True)
class VarTerm:
    """Represent a logical variable (uppercase identifier) before rule grounding."""

    name: str


@dataclass(frozen=True, slots=True)
class IntervalTerm:
    """Represent an integer range ``low..high`` before pool expansion."""

    low: RawTerm
    high: RawTerm


@dataclass(frozen=True, slots=True)
class PoolTerm:
    """Represent a semicolon-separated pool of alternative terms."""

    items: tuple[RawTerm, ...]


@dataclass(frozen=True, slots=True)
class FuncTerm:
    """Represent a function or tuple term in ASP."""

    name: str
    args: tuple[Term, ...] = ()


@dataclass(frozen=True, slots=True)
class RawFuncTerm:
    """Represent a function or tuple term that may still contain variables or pools."""

    name: str
    args: tuple[RawTerm, ...] = ()


type Term = NumberTerm | StringTerm | FuncTerm
type RawTerm = NumberTerm | StringTerm | VarTerm | IntervalTerm | PoolTerm | RawFuncTerm


@dataclass(frozen=True, slots=True)
class RawAssignment:
    """Represent a ``VAR = EXPR`` unification literal in a rule body."""

    var_name: str
    expr: RawTerm


@dataclass(frozen=True, slots=True)
class RawRule:
    """Represent a parsed ASP fact or ``Head :- VAR = EXPR, ... .`` rule."""

    head: RawFuncTerm
    assignments: tuple[RawAssignment, ...] = ()


@dataclass(frozen=True, slots=True)
class StmtNoop:
    """Represent a ``noop`` statement."""


@dataclass(frozen=True, slots=True)
class StmtAssert:
    """Represent an ``assert(E)`` statement."""

    expr: Term


@dataclass(frozen=True, slots=True)
class StmtAssign:
    """Represent an ``assign(X, E)`` statement."""

    var: Term
    expr: Term


@dataclass(frozen=True, slots=True)
class StmtIf:
    """Represent an ``if(COND, THEN, ELSE)`` statement."""

    cond: Term
    then_branch: Stmt
    else_branch: Stmt


@dataclass(frozen=True, slots=True)
class StmtSeq2:
    """Represent a ``seq2(S1, S2)`` sequential composition statement."""

    first: Stmt
    second: Stmt


@dataclass(frozen=True, slots=True)
class StmtPython:
    """Represent a ``statement_python(CODE)`` statement."""

    code: str


type Stmt = StmtNoop | StmtAssert | StmtAssign | StmtIf | StmtSeq2 | StmtPython


_OPERATOR_MAP: dict[str, Operator] = {
    "eq": Operator.eq,
    "neq": Operator.neq,
    "concat": Operator.concat,
    "length": Operator.length,
    "max": Operator.max,
    "min": Operator.min,
    "getOrElse": Operator.get_or_else,
    "get_or_else": Operator.get_or_else,
    "if": Operator.if_,
    "if_": Operator.if_,
    "hasValue": Operator.has_value,
    "has_value": Operator.has_value,
    "abs": Operator.abs,
    "sqrt": Operator.sqrt,
    "cos": Operator.cos,
    "sin": Operator.sin,
    "tan": Operator.tan,
    "acos": Operator.acos,
    "asin": Operator.asin,
    "atan": Operator.atan,
    "minus": Operator.minus,
    "mod": Operator.mod,
    "floor": Operator.floor,
    "ceil": Operator.ceil,
    "add": Operator.add,
    "sub": Operator.sub,
    "mult": Operator.mult,
    "int_div": Operator.int_div,
    "float_div": Operator.real_div,
    "pow": Operator.pow,
    "leq": Operator.leq,
    "lt": Operator.lt,
    "geq": Operator.geq,
    "gt": Operator.gt,
    "float_from_int": Operator.real_from_int,
    "int_from_float": Operator.int_from_real,
    "conj": Operator.conj,
    "disj": Operator.disj,
    "ite": Operator.ite,
    "leqv": Operator.leqv,
    "limp": Operator.limp,
    "lnot": Operator.lnot,
    "lxor": Operator.lxor,
    "snot": Operator.snot,
    "wnot": Operator.wnot,
    "cardinality": Operator.cardinality,
    "set_make": Operator.set_make,
    "set_isin": Operator.set_isin,
    "set_notin": Operator.set_notin,
    "union": Operator.union,
    "inter": Operator.inter,
    "diff": Operator.diff,
    "subset": Operator.subset,
    "set_fold": Operator.set_fold,
    "tuple_get": Operator.tuple_get,
}

_UNSUPPORTED_OPERATORS: frozenset[str] = frozenset(
    {
        "find",
        "find2",
        "multimap_isin",
        "multimap_make",
        "multimap_fold",
        "multimap_fold_i",
        "countKeys",
        "countEntries",
        "sumIntEntries",
        "maxEntries",
        "minEntries",
        "pythonExtract",
    }
)

_UNSUPPORTED_PREDICATES: frozenset[str] = frozenset(
    {
        "multimap_assign",
        "optimize_precision",
        "preference_maximizeScore",
        "preference_holds",
        "preference_variableValue",
        "warning_forbid",
        "warning_ignore",
        "default_mode",
    }
)

_IGNORED_PREDICATES: frozenset[str] = frozenset({"phase_request"})


@dataclass(frozen=True, slots=True)
class _Token:
    """Store one lexical token from an ASP input source."""

    kind: str
    value: str
    pos: int


def _tokenize(source: str) -> list[_Token]:
    """Tokenize ASP facts, rules, directives, and comments."""
    tokens: list[_Token] = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if source.startswith("%*", i):
            end = source.find("*%", i + 2)
            if end == -1:
                raise ConversionError(f"Unterminated block comment at position {i}")
            i = end + 2
            continue
        if ch == "%":
            end = source.find("\n", i + 1)
            i = n if end == -1 else end + 1
            continue
        if source.startswith(":-", i):
            tokens.append(_Token(" NECK ", ":-", i))
            i += 2
            continue
        if source.startswith("..", i):
            tokens.append(_Token("DOTDOT", "..", i))
            i += 2
            continue
        if ch in "(),.;={}:/@":
            tokens.append(_Token(ch, ch, i))
            i += 1
            continue
        if ch == '"':
            start = i
            i += 1
            chars: list[str] = []
            while i < n and source[i] != '"':
                if source[i] == "\\":
                    i += 1
                    if i >= n:
                        raise ConversionError(f"Unterminated string literal at {start}")
                    esc = source[i]
                    escape_map = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
                    chars.append(escape_map.get(esc, "\\" + esc))
                else:
                    chars.append(source[i])
                i += 1
            if i >= n:
                raise ConversionError(f"Unterminated string literal at {start}")
            i += 1
            tokens.append(_Token("STRING", "".join(chars), start))
            continue
        if ch == "-" and i + 1 < n and source[i + 1].isdigit():
            start = i
            i += 1
            while i < n and source[i].isdigit():
                i += 1
            tokens.append(_Token("NUMBER", source[start:i], start))
            continue
        if ch.isdigit():
            start = i
            while i < n and source[i].isdigit():
                i += 1
            tokens.append(_Token("NUMBER", source[start:i], start))
            continue
        if ch == "#" or ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            ident = source[start:i]
            tokens.append(_Token("IDENT", ident, start))
            continue
        raise ConversionError(f"Unexpected character {ch!r} at position {i}")
    tokens.append(_Token("EOF", "", n))
    return tokens


def _is_logic_variable(ident: str) -> bool:
    """Return True when an identifier is an ASP logical variable."""
    stripped = ident.lstrip("_")
    return bool(stripped) and stripped[0].isupper()


class _Parser:
    """Parse tokenized ASP facts and simple assignment-body rules."""

    def __init__(self, tokens: list[_Token]) -> None:
        """Initialize parser state over a token list."""
        self._tokens = tokens
        self._pos = 0

    def _peek(self) -> _Token:
        """Return the current token without consuming it."""
        return self._tokens[self._pos]

    def _advance(self) -> _Token:
        """Consume and return the current token."""
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, kind: str) -> _Token:
        """Consume a token of the expected kind or raise ConversionError."""
        tok = self._peek()
        if tok.kind != kind:
            raise ConversionError(
                f"Expected {kind!r} but got {tok.value!r} at position {tok.pos}"
            )
        return self._advance()

    def parse_program(self) -> list[RawRule]:
        """Parse all statements in the token stream."""
        rules: list[RawRule] = []
        while self._peek().kind != "EOF":
            tok = self._peek()
            if tok.kind == "IDENT" and tok.value.startswith("#"):
                self._parse_directive()
                continue
            if tok.kind in ("{", "NUMBER"):
                raise UnsupportedFeatureError(
                    f"Choice rules are not supported (at position {tok.pos})"
                )
            rules.append(self._parse_rule())
        return rules

    def _parse_directive(self) -> None:
        """Handle or skip `#`-prefixed ASP directives up to the terminating dot."""
        directive = self._advance().value
        if directive in ("#maximize", "#minimize", "#heuristic"):
            raise UnsupportedFeatureError(
                f"Directive {directive} is not supported in ConstraintStore"
            )
        while self._peek().kind not in (".", "EOF"):
            self._advance()
        self._expect(".")

    def _parse_rule(self) -> RawRule:
        """Parse a ground fact or a rule with ``VAR = TERM`` assignments."""
        head_term = self._parse_atom()
        if self._peek().kind == ".":
            self._advance()
            return RawRule(head_term, ())
        if self._peek().kind == " NECK ":
            self._advance()
            assignments: list[RawAssignment] = [self._parse_body_literal()]
            while self._peek().kind == ",":
                self._advance()
                assignments.append(self._parse_body_literal())
            self._expect(".")
            return RawRule(head_term, tuple(assignments))
        tok = self._peek()
        raise ConversionError(
            f"Unexpected token {tok.value!r} in rule at position {tok.pos}"
        )

    def _parse_body_literal(self) -> RawAssignment:
        """Parse a ``VAR = TERM`` body literal or raise UnsupportedFeatureError."""
        tok = self._peek()
        if tok.kind == "IDENT" and _is_logic_variable(tok.value):
            var_name = self._advance().value
            if self._peek().kind == "=":
                self._advance()
                rhs = self._parse_term()
                return RawAssignment(var_name, rhs)
        raise UnsupportedFeatureError(
            f"General ASP rule bodies are not supported (at position {tok.pos})"
        )

    def _parse_atom(self) -> RawFuncTerm:
        """Parse a top-level predicate atom."""
        name_tok = self._expect("IDENT")
        if _is_logic_variable(name_tok.value):
            raise ConversionError(
                f"Predicate name cannot be a variable {name_tok.value!r} at {name_tok.pos}"
            )
        if self._peek().kind != "(":
            return RawFuncTerm(name_tok.value, ())
        self._advance()
        if self._peek().kind == ")":
            self._advance()
            return RawFuncTerm(name_tok.value, ())
        args = self._parse_arg_list()
        self._expect(")")
        return RawFuncTerm(name_tok.value, tuple(args))

    def _parse_arg_list(self) -> list[RawTerm]:
        """Parse comma-separated argument terms, allowing semicolon pools."""
        args: list[RawTerm] = [self._parse_pool_term()]
        while self._peek().kind == ",":
            self._advance()
            args.append(self._parse_pool_term())
        return args

    def _parse_pool_term(self) -> RawTerm:
        """Parse one term or a ``;``-separated pool of terms."""
        first = self._parse_term()
        if self._peek().kind != ";":
            return first
        items: list[RawTerm] = [first]
        while self._peek().kind == ";":
            self._advance()
            items.append(self._parse_term())
        return PoolTerm(tuple(items))

    def _parse_term(self) -> RawTerm:
        """Parse a single term, including intervals ``low..high``."""
        left = self._parse_primary_term()
        if self._peek().kind == "DOTDOT":
            self._advance()
            right = self._parse_primary_term()
            return IntervalTerm(left, right)
        return left

    def _parse_primary_term(self) -> RawTerm:
        """Parse a number, string, variable, tuple, parenthesized pool, or function term."""
        tok = self._peek()
        if tok.kind == "NUMBER":
            self._advance()
            return NumberTerm(int(tok.value))
        if tok.kind == "STRING":
            self._advance()
            return StringTerm(tok.value)
        if tok.kind == "IDENT":
            self._advance()
            if _is_logic_variable(tok.value):
                return VarTerm(tok.value)
            if self._peek().kind != "(":
                return RawFuncTerm(tok.value, ())
            self._advance()
            if self._peek().kind == ")":
                self._advance()
                return RawFuncTerm(tok.value, ())
            args = self._parse_arg_list()
            self._expect(")")
            return RawFuncTerm(tok.value, tuple(args))
        if tok.kind == "(":
            self._advance()
            if self._peek().kind == ")":
                self._advance()
                return RawFuncTerm("", ())
            first = self._parse_pool_term()
            if self._peek().kind == ")":
                self._advance()
                if isinstance(first, PoolTerm):
                    return first
                return RawFuncTerm("", (first,))
            items: list[RawTerm] = [first]
            while self._peek().kind == ",":
                self._advance()
                if self._peek().kind == ")":
                    break
                items.append(self._parse_pool_term())
            self._expect(")")
            return RawFuncTerm("", tuple(items))
        raise ConversionError(
            f"Unexpected token {tok.value!r} ({tok.kind}) at position {tok.pos}"
        )


def _expand_raw_term(raw: RawTerm, bindings: dict[str, Term]) -> list[Term]:
    """Substitute logical variables and expand pools and intervals into ground terms."""
    match raw:
        case NumberTerm() | StringTerm():
            return [raw]
        case VarTerm(name):
            if name not in bindings:
                raise ConversionError(f"Unbound logical variable {name!r}")
            return [bindings[name]]
        case IntervalTerm(low_raw, high_raw):
            lows = _expand_raw_term(low_raw, bindings)
            highs = _expand_raw_term(high_raw, bindings)
            results: list[Term] = []
            for low_term in lows:
                for high_term in highs:
                    if not isinstance(low_term, NumberTerm) or not isinstance(
                        high_term, NumberTerm
                    ):
                        raise ConversionError("Interval bounds must be integers")
                    for val in range(low_term.value, high_term.value + 1):
                        results.append(NumberTerm(val))
            return results
        case PoolTerm(items):
            expanded: list[Term] = []
            for item in items:
                expanded.extend(_expand_raw_term(item, bindings))
            return expanded
        case RawFuncTerm(name, args):
            arg_choices: list[list[Term]] = [[]]
            for arg in args:
                expanded_arg = _expand_raw_term(arg, bindings)
                arg_choices = [
                    [*prefix, choice]
                    for prefix in arg_choices
                    for choice in expanded_arg
                ]
            return [FuncTerm(name, tuple(choice)) for choice in arg_choices]


def _raw_vars(raw: RawTerm) -> set[str]:
    """Return all logical variable names referenced inside a RawTerm."""
    match raw:
        case NumberTerm() | StringTerm():
            return set()
        case VarTerm(name):
            return {name}
        case IntervalTerm(low, high):
            return _raw_vars(low) | _raw_vars(high)
        case PoolTerm(items):
            pool_vars: set[str] = set()
            for item in items:
                pool_vars |= _raw_vars(item)
            return pool_vars
        case RawFuncTerm(_, args):
            func_vars: set[str] = set()
            for arg in args:
                func_vars |= _raw_vars(arg)
            return func_vars


def _ground_rule(rule: RawRule) -> list[FuncTerm]:
    """Resolve ``VAR = TERM`` assignments in topological order and expand the rule head."""
    pending = list(rule.assignments)
    envs: list[dict[str, Term]] = [{}]
    while pending:
        resolved_any = False
        for idx, assignment in enumerate(pending):
            needed = _raw_vars(assignment.expr)
            if all(var in envs[0] for var in needed):
                pending.pop(idx)
                new_envs: list[dict[str, Term]] = []
                for env in envs:
                    for val in _expand_raw_term(assignment.expr, env):
                        if (
                            assignment.var_name in env
                            and env[assignment.var_name] != val
                        ):
                            continue
                        next_env = dict(env)
                        next_env[assignment.var_name] = val
                        new_envs.append(next_env)
                envs = new_envs
                resolved_any = True
                break
        if not resolved_any:
            unresolved = [a.var_name for a in pending]
            raise ConversionError(f"Cyclic or unresolved rule variables: {unresolved}")
    atoms: list[FuncTerm] = []
    for env in envs:
        for term in _expand_raw_term(rule.head, env):
            assert isinstance(term, FuncTerm)
            atoms.append(term)
    return atoms


def _term_to_str(term: Term) -> str:
    """Format a ground Term into its canonical Clingo string representation."""
    match term:
        case NumberTerm(val):
            return str(val)
        case StringTerm(val):
            escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'"{escaped}"'
        case FuncTerm("", args):
            if not args:
                return "()"
            if len(args) == 1:
                return f"({_term_to_str(args[0])},)"
            return f"({','.join(_term_to_str(a) for a in args)})"
        case FuncTerm(name, ()):
            return name
        case FuncTerm(name, args):
            return f"{name}({','.join(_term_to_str(a) for a in args)})"


def _var_term_to_name(term: Term) -> str:
    """Convert an ASP variable identifier term into a VariableRef string name."""
    if term in (StringTerm("__fail"), FuncTerm("__fail", ())):
        raise ConversionError("Variable name '__fail' is reserved by the converter")
    match term:
        case StringTerm(val):
            return val
        case _:
            return _term_to_str(term)


def _label_term_to_str(term: Term | None, default: str = LABEL_ANONYMOUS) -> str:
    """Convert an optional ASP label term into a ConstraintStore label string."""
    if term is None:
        return default
    if isinstance(term, FuncTerm) and term.name == "_label_anonymous" and not term.args:
        return LABEL_ANONYMOUS
    if isinstance(term, StringTerm):
        return term.value
    return _term_to_str(term)


def _unnest_list(term: Term) -> list[Term]:
    """Unpack a right-nested ASP linked list ``(a, (b, ()))`` into a Python list."""
    items: list[Term] = []
    curr = term
    while True:
        if isinstance(curr, FuncTerm) and curr.name == "" and len(curr.args) == 0:
            return items
        if isinstance(curr, FuncTerm) and curr.name == "" and len(curr.args) == 2:
            items.append(curr.args[0])
            curr = curr.args[1]
        else:
            raise ConversionError(
                f"Expected right-nested list term, got {_term_to_str(term)}"
            )


def _parse_float_arg(term: Term) -> float:
    """Extract a Python float from ``float("1.5")``, ``"1.5"``, or an integer term."""
    match term:
        case NumberTerm(val):
            return float(val)
        case StringTerm(val):
            return float(val)
        case FuncTerm("float", (arg,)):
            return _parse_float_arg(arg)
        case _:
            raise ConversionError(f"Invalid float literal term: {_term_to_str(term)}")


def _convert_val(type_term: Term, val_term: Term) -> Expr:
    """Convert ``val(TYPE, VALUE)`` into a Python input scalar."""
    if not isinstance(type_term, FuncTerm) or type_term.args:
        raise ConversionError(f"Invalid value type term: {_term_to_str(type_term)}")
    type_name = type_term.name
    match type_name:
        case "bool":
            if isinstance(val_term, FuncTerm) and not val_term.args:
                if val_term.name == "true":
                    return True
                if val_term.name == "false":
                    return False
            raise ConversionError(f"Invalid bool literal: {_term_to_str(val_term)}")
        case "int":
            if isinstance(val_term, NumberTerm):
                return val_term.value
            raise ConversionError(f"Invalid int literal: {_term_to_str(val_term)}")
        case "float":
            return _parse_float_arg(val_term)
        case "string":
            if isinstance(val_term, StringTerm):
                return val_term.value
            raise ConversionError(f"Invalid string literal: {_term_to_str(val_term)}")
        case "none":
            if (
                isinstance(val_term, FuncTerm)
                and val_term.name == "none"
                and not val_term.args
            ):
                return None
            raise ConversionError(f"Invalid none literal: {_term_to_str(val_term)}")
        case _:
            raise UnsupportedFeatureError(
                f"Unsupported value type {type_name!r} in val({_term_to_str(type_term)}, {_term_to_str(val_term)})"
            )


def _convert_lambda(
    term: FuncTerm, env: dict[Term, VariableRef] | None = None
) -> Lambda:
    """Convert ``lambda(VARS, BODY)`` into a ``python_input.Lambda``."""
    if len(term.args) != 2:
        raise ConversionError(f"Malformed lambda expression: {_term_to_str(term)}")
    raw_vars = _unnest_list(term.args[0])
    params = tuple(VariableRef(_var_term_to_name(v)) for v in raw_vars)
    shadowed_env: dict[Term, VariableRef] | None = None
    if env is not None:
        shadowed_env = dict(env)
        for v in raw_vars:
            shadowed_env[v] = VariableRef(_var_term_to_name(v))
    body = _convert_expr(term.args[1], shadowed_env)
    return Lambda(params, body)


def _convert_arg(
    term: Term,
    env: dict[Term, VariableRef] | None = None,
    default_prg: Term | None = None,
) -> OperationArg:
    """Convert an operation argument into a value expression or lambda descriptor."""
    if isinstance(term, FuncTerm) and term.name == "lambda" and len(term.args) == 2:
        return _convert_lambda(term, env)
    return _convert_expr(term, env, default_prg)


def _convert_expr(
    term: Term,
    env: dict[Term, VariableRef] | None = None,
    default_prg: Term | None = None,
) -> Expr:
    """Convert an old ASP expression term into a ``python_input.Expr``."""
    match term:
        case NumberTerm(val):
            return val
        case StringTerm(val):
            return val
        case FuncTerm("bad", ()):
            raise UnsupportedFeatureError("The 'bad' literal is not supported")
        case FuncTerm("true", ()):
            return True
        case FuncTerm("false", ()):
            return False
        case FuncTerm("float", (arg,)):
            return _parse_float_arg(arg)
        case FuncTerm("val", (type_term, val_term)):
            return _convert_val(type_term, val_term)
        case FuncTerm("variable", (var_term,)):
            if env is not None:
                if var_term in env:
                    return env[var_term]
                if default_prg is not None:
                    implicit_in = FuncTerm("execution_input", (default_prg, var_term))
                    return VariableRef(_var_term_to_name(implicit_in))
            return VariableRef(_var_term_to_name(var_term))
        case FuncTerm("python", (StringTerm(code),)):
            return Operation(Operator.python_eval, (Python(f"lambda: ({code}\n)"),))
        case FuncTerm("lambda", (_, _)):
            return Operation(Operator.lambda_, (_convert_lambda(term, env),))
        case FuncTerm("operation", (op_term, args_list_term)):
            raw_args = _unnest_list(args_list_term)
            converted_args = tuple(
                _convert_arg(arg, env, default_prg) for arg in raw_args
            )
            return _convert_operation(op_term, converted_args, env, default_prg)
        case FuncTerm("", args):
            return tuple(_convert_expr(a, env, default_prg) for a in args)
        case FuncTerm(name, ()):
            raise UnsupportedFeatureError(f"Symbol {name!r} is not supported")
        case FuncTerm(name, args):
            if name in _OPERATOR_MAP or name in _UNSUPPORTED_OPERATORS:
                converted_args = tuple(
                    _convert_arg(arg, env, default_prg) for arg in args
                )
                return _convert_operation(
                    FuncTerm(name, ()), converted_args, env, default_prg
                )
            raise ConversionError(f"Unrecognized expression term: {_term_to_str(term)}")


def _convert_operation(
    op_term: Term,
    converted_args: tuple[OperationArg, ...],
    env: dict[Term, VariableRef] | None = None,
    default_prg: Term | None = None,
) -> Operation:
    """Convert an operation's operator term and arguments into an Operation."""
    match op_term:
        case FuncTerm("python", (StringTerm(code),)):
            return Operation(Operator.python_eval, (Python(code), *converted_args))
        case FuncTerm("pythonExtract", _):
            raise UnsupportedFeatureError("Operator 'pythonExtract' is not supported")
        case FuncTerm("lambda", (_, _)):
            lam = _convert_lambda(op_term, env)
            return Operation(Operator.lambda_, (lam, *converted_args))
        case FuncTerm("variable", (_var_term,)):
            var_ref = _convert_expr(op_term, env, default_prg)
            return Operation(Operator.lambda_, (var_ref, *converted_args))
        case FuncTerm(op_name, ()):
            if op_name in _UNSUPPORTED_OPERATORS:
                raise UnsupportedFeatureError(
                    f"Operator {op_name!r} is not supported in ConstraintStore"
                )
            if op_name not in _OPERATOR_MAP:
                raise UnsupportedFeatureError(f"Unknown operator {op_name!r}")
            return Operation(_OPERATOR_MAP[op_name], converted_args)
        case _:
            raise ConversionError(
                f"Invalid operator term in operation: {_term_to_str(op_term)}"
            )


def _parse_stmt(term: Term) -> Stmt:
    """Parse an ASP statement term into a structured Stmt AST."""
    match term:
        case FuncTerm("noop", ()):
            return StmtNoop()
        case FuncTerm("assert", (expr_term,)):
            return StmtAssert(expr_term)
        case FuncTerm("assign", (var_term, expr_term)):
            return StmtAssign(var_term, expr_term)
        case FuncTerm("if", (cond_term, then_term, else_term)):
            return StmtIf(cond_term, _parse_stmt(then_term), _parse_stmt(else_term))
        case FuncTerm("seq2", (first_term, second_term)):
            return StmtSeq2(_parse_stmt(first_term), _parse_stmt(second_term))
        case FuncTerm("statement_python", (StringTerm(code),)):
            _analyze_python_code(code)
            return StmtPython(code)
        case FuncTerm("while", _):
            raise UnsupportedFeatureError(
                "While statements are not supported in ConstraintStore"
            )
        case _:
            raise ConversionError(f"Invalid statement term: {_term_to_str(term)}")


def _collect_expr_var_terms(term: Term) -> set[Term]:
    """Collect all ``Term`` identifiers referenced inside ``variable(X)`` in an expression."""
    match term:
        case NumberTerm() | StringTerm():
            return set()
        case FuncTerm("variable", (var_term,)):
            return {var_term}
        case FuncTerm("lambda", (vars_list, body)):
            bound = set(_unnest_list(vars_list))
            return _collect_expr_var_terms(body) - bound
        case FuncTerm(_, args):
            result: set[Term] = set()
            for arg in args:
                result |= _collect_expr_var_terms(arg)
            return result


class _PythonStmtAnalysis(ast.NodeVisitor):
    """Extract assigned and loaded names from Python code."""

    def __init__(self) -> None:
        """Initialize analysis sets."""
        self.assigned: list[str] = []
        self.loaded: set[str] = set()

    def _record_assigned(self, name: str) -> None:
        """Record an assigned variable name in order of first appearance."""
        if name not in self.assigned:
            self.assigned.append(name)

    def visit_Name(self, node: ast.Name) -> None:
        """Track store and load variable contexts."""
        if node.id == "__fail":
            raise ConversionError("Variable name '__fail' is reserved by the converter")
        if isinstance(node.ctx, ast.Store):
            self._record_assigned(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.loaded.add(node.id)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Track augmented assignments (which both load and store their target)."""
        if isinstance(node.target, ast.Name):
            self.visit(node.target)
            self.loaded.add(node.target.id)
        self.visit(node.value)


def _analyze_python_code(code: str) -> _PythonStmtAnalysis:
    """Parse Python statement code and return its static variable analysis."""
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise ConversionError(f"Syntax error in statement_python: {exc}") from exc
    analyzer = _PythonStmtAnalysis()
    analyzer.visit(tree)
    return analyzer


def _execute_python_statement(
    code: str,
    inputs: dict[str, object],
    output_names: tuple[str, ...],
    context: dict[str, object],
) -> tuple[object, ...]:
    """Execute a legacy statement, returning a failure flag followed by its outputs."""

    def constrain(condition: object) -> None:
        """Signal a deliberate statement failure when the condition is false."""
        if not condition:
            raise FailIntegrityExn

    environment = {
        **context,
        "FailIntegrityExn": FailIntegrityExn,
        "constrain": constrain,
        "solver_environment": SimpleNamespace(
            FailIntegrityExn=FailIntegrityExn, constrain=constrain
        ),
    }
    try:
        exec(code, environment, inputs)  # noqa: S102
    except FailIntegrityExn:
        return (True, *(None for _ in output_names))
    return (False, *(inputs[name] for name in output_names))


def _build_python_callable(
    code: str, input_names: list[str], output_names: list[str]
) -> str:
    """Build a statement callback returning its failure flag and live outputs."""
    params = ", ".join(input_names)
    dict_items = ", ".join(f"{name!r}: {name}" for name in input_names)
    return (
        f"(lambda {params}: "
        f"__import__('scratch.converter.converter', fromlist=['_execute_python_statement'])"
        f"._execute_python_statement({code!r}, {{{dict_items}}}, {tuple(output_names)!r}, globals()))"
    )


def _make_condition(conds: tuple[Expr, ...]) -> Expr:
    """Combine path conditions into a single boolean expression."""
    if not conds:
        return True
    result = conds[-1]
    for cond in reversed(conds[:-1]):
        result = Operation(Operator.conj, (cond, result))
    return result


class _SSAConverter:
    """Convert an ``execution_declare`` statement tree into SSA definitions on a ConstraintStore."""

    def __init__(
        self,
        store: ConstraintStore,
        prg: Term,
        label: str,
        inputs: list[Term],
        outputs: list[Term],
    ) -> None:
        """Initialize the SSA converter for a single execution declaration."""
        self._store = store
        self._prg = prg
        self._prg_str = _term_to_str(prg)
        self._label = label
        self._inputs = inputs
        self._outputs = outputs
        self._counter = 0
        for variable in (*inputs, *outputs):
            _var_term_to_name(variable)

    def _fresh_var(self, base: str, scope: str) -> VariableRef:
        """Create a unique SSA local VariableRef."""
        self._counter += 1
        suffix = f"_{scope}" if scope else f"_{self._counter}"
        return VariableRef(f"loc({self._prg_str}_{base}{suffix})")

    def _compute_live_before(self, stmt: Stmt, live_after: set[Term]) -> set[Term]:
        """Compute variables needed before executing ``stmt`` given ``live_after``."""
        match stmt:
            case StmtNoop():
                return set(live_after)
            case StmtAssert(expr):
                return set(live_after) | _collect_expr_var_terms(expr)
            case StmtAssign(var, expr):
                return (set(live_after) - {var}) | _collect_expr_var_terms(expr)
            case StmtIf(cond, then_b, else_b):
                live_then = self._compute_live_before(then_b, live_after)
                live_else = self._compute_live_before(else_b, live_after)
                return _collect_expr_var_terms(cond) | live_then | live_else
            case StmtSeq2(first, second):
                live_mid = self._compute_live_before(second, live_after)
                return self._compute_live_before(first, live_mid)
            case StmtPython(code):
                analysis = _analyze_python_code(code)
                assigned_terms = {StringTerm(name) for name in analysis.assigned}
                loaded_terms = {StringTerm(name) for name in analysis.loaded}
                return (set(live_after) - assigned_terms) | loaded_terms

    def _collect_modified(self, stmt: Stmt, live_after: set[Term]) -> list[Term]:
        """Return variables modified by ``stmt`` that are live afterward."""
        match stmt:
            case StmtNoop() | StmtAssert():
                return []
            case StmtAssign(var, _):
                return [var]
            case StmtIf(_, then_b, else_b):
                mod_then = self._collect_modified(then_b, live_after)
                mod_else = self._collect_modified(else_b, live_after)
                seen: list[Term] = []
                for v in (*mod_then, *mod_else):
                    if v not in seen:
                        seen.append(v)
                return seen
            case StmtSeq2(first, second):
                live_mid = self._compute_live_before(second, live_after)
                mod_first = self._collect_modified(first, live_mid)
                mod_second = self._collect_modified(second, live_after)
                seen = []
                for v in (*mod_first, *mod_second):
                    if v not in seen:
                        seen.append(v)
                return seen
            case StmtPython(code):
                analysis = _analyze_python_code(code)
                return [
                    StringTerm(name)
                    for name in analysis.assigned
                    if StringTerm(name) in live_after
                ]

    def convert(self, stmt: Stmt, is_running: bool) -> None:
        """Convert the execution statement and bind ``execution_output(PRG, X)`` variables."""
        if not is_running:
            for out_var in self._outputs:
                out_term = FuncTerm("execution_output", (self._prg, out_var))
                self._store.define(
                    VariableRef(_var_term_to_name(out_term)),
                    None,
                    label=self._label,
                )
            return

        env: dict[Term, VariableRef] = {}
        for in_var in self._inputs:
            in_term = FuncTerm("execution_input", (self._prg, in_var))
            in_ref = VariableRef(_var_term_to_name(in_term))
            self._store.variables.setdefault(in_ref, Variable())
            env[in_var] = in_ref

        live_out = set(self._outputs)
        final_env = self._convert_stmt(stmt, env, (), "", live_out)

        for out_var in self._outputs:
            out_term = FuncTerm("execution_output", (self._prg, out_var))
            out_ref = VariableRef(_var_term_to_name(out_term))
            val_expr: Expr = final_env.get(out_var, None)
            self._store.define(out_ref, val_expr, label=self._label)

    def _convert_stmt(
        self,
        stmt: Stmt,
        env: dict[Term, VariableRef],
        conds: tuple[Expr, ...],
        scope: str,
        live_after: set[Term],
    ) -> dict[Term, VariableRef]:
        """Recursively translate ``stmt`` into SSA definitions and checks."""
        match stmt:
            case StmtNoop():
                return dict(env)

            case StmtAssert(expr_term):
                expr = _convert_expr(expr_term, env, self._prg)
                if conds:
                    cond_expr = _make_condition(conds)
                    check_expr: Expr = Operation(Operator.limp, (cond_expr, expr))
                else:
                    check_expr = expr
                self._store.check(check_expr, label=self._label)
                return dict(env)

            case StmtAssign(var_term, expr_term):
                rhs = _convert_expr(expr_term, env, self._prg)
                ssa_var = self._fresh_var(_var_term_to_name(var_term), scope)
                self._store.define(
                    ssa_var,
                    rhs,
                    condition=_make_condition(conds),
                    label=self._label,
                )
                next_env = dict(env)
                next_env[var_term] = ssa_var
                return next_env

            case StmtSeq2(first, second):
                live_mid = self._compute_live_before(second, live_after)
                mid_env = self._convert_stmt(first, env, conds, scope + "l", live_mid)
                return self._convert_stmt(
                    second, mid_env, conds, scope + "r", live_after
                )

            case StmtIf(cond_term, then_branch, else_branch):
                cond_expr = _convert_expr(cond_term, env, self._prg)
                neg_cond_expr = Operation(Operator.lnot, (cond_expr,))
                then_conds = (*conds, cond_expr)
                else_conds = (*conds, neg_cond_expr)

                then_env = self._convert_stmt(
                    then_branch, env, then_conds, scope + "t", live_after
                )
                else_env = self._convert_stmt(
                    else_branch, env, else_conds, scope + "e", live_after
                )

                modified = self._collect_modified(stmt, live_after)
                merged_env = dict(env)
                for var_term in modified:
                    merged_var = self._fresh_var(_var_term_to_name(var_term), scope)
                    then_val: Expr = then_env.get(var_term, None)
                    else_val: Expr = else_env.get(var_term, None)
                    self._store.define(
                        merged_var,
                        then_val,
                        condition=_make_condition(then_conds),
                        label=self._label,
                    )
                    self._store.define(
                        merged_var,
                        else_val,
                        condition=_make_condition(else_conds),
                        label=self._label,
                    )
                    merged_env[var_term] = merged_var
                return merged_env

            case StmtPython(code):
                analysis = _analyze_python_code(code)
                string_vars = sorted(
                    term.value for term in env if isinstance(term, StringTerm)
                )
                input_args = tuple(env[StringTerm(name)] for name in string_vars)
                needed_outputs = [
                    name for name in analysis.assigned if StringTerm(name) in live_after
                ]
                cond_expr = _make_condition(conds)
                fn_str = _build_python_callable(code, string_vars, needed_outputs)
                tuple_var = self._fresh_var("_py_tuple", scope)
                self._store.define(
                    tuple_var,
                    Operation(Operator.python_eval, (Python(fn_str), *input_args)),
                    condition=cond_expr,
                    label=self._label,
                )
                failed = Operation(Operator.tuple_get, (tuple_var, 0))
                self._store.define(
                    VariableRef("__fail"),
                    True,
                    condition=Operation(Operator.conj, (cond_expr, failed)),
                    label=self._label,
                )
                next_env = dict(env)
                for idx, out_name in enumerate(needed_outputs, start=1):
                    out_ssa_var = self._fresh_var(out_name, scope)
                    self._store.define(
                        out_ssa_var,
                        Operation(Operator.tuple_get, (tuple_var, idx)),
                        condition=cond_expr,
                        label=self._label,
                    )
                    next_env[StringTerm(out_name)] = out_ssa_var
                return next_env


def convert_string(source: str) -> ConstraintStore:
    """Parse old constraint-handler ASP facts/rules and populate a new ConstraintStore."""
    tokens = _tokenize(source)
    raw_rules = _Parser(tokens).parse_program()
    atoms: list[FuncTerm] = []
    for rule in raw_rules:
        atoms.extend(_ground_rule(rule))

    store = ConstraintStore()

    declared_labels: dict[Term, str] = {}
    declared_domains: dict[Term, tuple[str, str]] = {}
    variables_with_entries: set[Term] = set()
    sets_with_entries: set[Term] = set()
    running_executions: set[Term] = set()
    executions: list[tuple[Term, Stmt, list[Term], list[Term], str]] = []
    eval_counter = 0
    objective_counter = 0
    bool_eval_counter = 0

    for atom in atoms:
        if atom.name in _IGNORED_PREDICATES:
            continue
        if atom.name in _UNSUPPORTED_PREDICATES:
            raise UnsupportedFeatureError(
                f"Predicate {atom.name!r} is not supported in ConstraintStore"
            )
        if atom.name == "variable_declare":
            if len(atom.args) not in (2, 3):
                raise ConversionError(
                    f"Invalid arity for variable_declare: {_term_to_str(atom)}"
                )
            var_term = atom.args[0]
            dom_term = atom.args[1]
            lbl = _label_term_to_str(atom.args[2] if len(atom.args) == 3 else None)
            if not isinstance(dom_term, FuncTerm) or dom_term.args:
                raise ConversionError(
                    f"Invalid domain in variable_declare: {_term_to_str(atom)}"
                )
            if dom_term.name == "multimap":
                raise UnsupportedFeatureError(
                    "Domain 'multimap' is not supported in ConstraintStore"
                )
            if dom_term.name not in (
                "definition",
                "boolDomain",
                "fromFacts",
                "open",
                "set",
            ):
                raise ConversionError(
                    f"Unknown variable domain {dom_term.name!r} in {_term_to_str(atom)}"
                )
            declared_labels[var_term] = lbl
            declared_domains[var_term] = (dom_term.name, lbl)
        elif atom.name == "execution_run":
            if len(atom.args) not in (1, 2):
                raise ConversionError(
                    f"Invalid arity for execution_run: {_term_to_str(atom)}"
                )
            running_executions.add(atom.args[0])

    for var_term, (dom_name, lbl) in declared_domains.items():
        var_ref = VariableRef(_var_term_to_name(var_term))
        if dom_name == "boolDomain":
            store.choose_from_iterator(var_ref, (False, True), label=lbl)
            variables_with_entries.add(var_term)

    for atom in atoms:
        name = atom.name
        args = atom.args
        if name in _IGNORED_PREDICATES or name in ("variable_declare", "execution_run"):
            continue

        match name:
            case "variable_domain":
                if len(args) not in (2, 3):
                    raise ConversionError(
                        f"Invalid arity for variable_domain: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                default_lbl = declared_labels.get(var_term, LABEL_ANONYMOUS)
                lbl = _label_term_to_str(
                    args[2] if len(args) == 3 else None, default_lbl
                )
                store.choose_from_iterator(
                    VariableRef(_var_term_to_name(var_term)),
                    (_convert_expr(expr_term),),
                    label=lbl,
                )
                variables_with_entries.add(var_term)

            case "variable_choice":
                if len(args) not in (2, 3):
                    raise ConversionError(
                        f"Invalid arity for variable_choice: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                default_lbl = declared_labels.get(var_term, LABEL_ANONYMOUS)
                lbl = _label_term_to_str(
                    args[2] if len(args) == 3 else None, default_lbl
                )
                store.choose_from_iterator(
                    VariableRef(_var_term_to_name(var_term)),
                    (_convert_expr(expr_term),),
                    label=lbl,
                )
                variables_with_entries.add(var_term)

            case "variable_define" | "variable_assign":
                if len(args) not in (2, 3):
                    raise ConversionError(
                        f"Invalid arity for {name}: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                default_lbl = declared_labels.get(var_term, LABEL_ANONYMOUS)
                lbl = _label_term_to_str(
                    args[2] if len(args) == 3 else None, default_lbl
                )
                store.define(
                    VariableRef(_var_term_to_name(var_term)),
                    _convert_expr(expr_term),
                    label=lbl,
                )
                variables_with_entries.add(var_term)

            case "variable_default":
                if len(args) not in (2, 3, 4, 5):
                    raise ConversionError(
                        f"Invalid arity for variable_default: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                cond_expr: Expr = _convert_expr(args[2]) if len(args) >= 3 else True
                prio = 0
                if len(args) >= 4:
                    if not isinstance(args[3], NumberTerm):
                        raise ConversionError(
                            f"Priority in variable_default must be an integer: {_term_to_str(atom)}"
                        )
                    prio = args[3].value
                default_lbl = declared_labels.get(var_term, LABEL_ANONYMOUS)
                lbl = _label_term_to_str(
                    args[4] if len(args) == 5 else None, default_lbl
                )
                store.default_to(
                    VariableRef(_var_term_to_name(var_term)),
                    _convert_expr(expr_term),
                    condition=cond_expr,
                    priority=prio,
                    label=lbl,
                )
                variables_with_entries.add(var_term)

            case "set_baseDomain":
                if len(args) not in (2, 3):
                    raise ConversionError(
                        f"Invalid arity for set_baseDomain: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                lbl = _label_term_to_str(args[2] if len(args) == 3 else None)
                store.set_contain_choose_from_iterator(
                    VariableRef(_var_term_to_name(var_term)),
                    (_convert_expr(expr_term),),
                    label=lbl,
                )
                sets_with_entries.add(var_term)

            case "set_assign":
                if len(args) not in (2, 3, 4):
                    raise ConversionError(
                        f"Invalid arity for set_assign: {_term_to_str(atom)}"
                    )
                var_term, expr_term = args[0], args[1]
                cond_expr = _convert_expr(args[2]) if len(args) >= 3 else True
                lbl = _label_term_to_str(args[3] if len(args) == 4 else None)
                store.set_contain(
                    VariableRef(_var_term_to_name(var_term)),
                    _convert_expr(expr_term),
                    condition=cond_expr,
                    label=lbl,
                )
                sets_with_entries.add(var_term)

            case "ensure":
                if len(args) not in (1, 2):
                    raise ConversionError(
                        f"Invalid arity for ensure: {_term_to_str(atom)}"
                    )
                lbl = _label_term_to_str(args[1] if len(args) == 2 else None)
                store.check(_convert_expr(args[0]), label=lbl)

            case "evaluate":
                if len(args) not in (1, 2):
                    raise ConversionError(
                        f"Invalid arity for evaluate: {_term_to_str(atom)}"
                    )
                lbl = _label_term_to_str(args[1] if len(args) == 2 else None)
                eval_var = VariableRef(f"__evaluate_{eval_counter}")
                eval_counter += 1
                store.define(eval_var, _convert_expr(args[0]), label=lbl)

            case "optimize_maximizeSum":
                if len(args) != 4:
                    raise ConversionError(
                        f"Invalid arity for optimize_maximizeSum: {_term_to_str(atom)}"
                    )
                if not isinstance(args[2], NumberTerm):
                    raise ConversionError(
                        f"Priority in optimize_maximizeSum must be an integer: {_term_to_str(atom)}"
                    )
                lbl = _label_term_to_str(args[3])
                objective_var = VariableRef(f"__objective_{objective_counter}")
                objective_counter += 1
                store.define(objective_var, _convert_expr(args[0]), label=lbl)
                store.minimize(
                    Operation(Operator.minus, (objective_var,)),
                    priority=args[2].value,
                    label=lbl,
                )

            case "bool_evaluate":
                if len(args) not in (1, 2):
                    raise ConversionError(
                        f"Invalid arity for bool_evaluate: {_term_to_str(atom)}"
                    )
                lbl = _label_term_to_str(args[1] if len(args) == 2 else None)
                bool_eval_var = VariableRef(f"__bool_evaluate_{bool_eval_counter}")
                bool_eval_counter += 1
                store.define(bool_eval_var, _convert_expr(args[0]), label=lbl)

            case "execution_declare":
                if len(args) not in (4, 5):
                    raise ConversionError(
                        f"Invalid arity for execution_declare: {_term_to_str(atom)}"
                    )
                prg_term = args[0]
                stmt = _parse_stmt(args[1])
                ins = _unnest_list(args[2])
                outs = _unnest_list(args[3])
                default_lbl = _var_term_to_name(prg_term)
                lbl = _label_term_to_str(
                    args[4] if len(args) == 5 else None, default_lbl
                )
                executions.append((prg_term, stmt, ins, outs, lbl))

            case _:
                raise UnsupportedFeatureError(
                    f"Unknown or unsupported predicate {name!r} in {_term_to_str(atom)}"
                )

    for var_term, (dom_name, lbl) in declared_domains.items():
        var_ref = VariableRef(_var_term_to_name(var_term))
        if dom_name in ("fromFacts", "open") and var_term not in variables_with_entries:
            store.choose_from_iterator(var_ref, (), label=lbl)
        elif dom_name == "definition" and var_term not in variables_with_entries:
            store.variables.setdefault(var_ref, Variable())
        elif dom_name == "set" and var_term not in sets_with_entries:
            store.set_contain_choose_from_iterator(var_ref, (), label=lbl)
            store.set_variables.setdefault(var_ref, SetVariable())

    for prg_term, stmt, ins, outs, lbl in executions:
        is_running = prg_term in running_executions
        ssa = _SSAConverter(store, prg_term, lbl, ins, outs)
        ssa.convert(stmt, is_running)

    if VariableRef("__fail") in store.variables:
        store.check(Operation(Operator.lnot, (VariableRef("__fail"),)))

    return store


def convert_file(path: str | Path) -> ConstraintStore:
    """Read an old constraint-handler ``.lp`` file and convert it into a ConstraintStore."""
    file_path = Path(path)
    return convert_string(file_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point to convert an old ``.lp`` input file and print a summary."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python -m converter <input.lp>", file=sys.stderr)
        return 2
    store = convert_file(args[0])
    print(
        f"Converted {args[0]}: "
        f"{len(store.variables)} variables, "
        f"{len(store.set_variables)} set_variables, "
        f"{len(store.constraints)} constraints"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
