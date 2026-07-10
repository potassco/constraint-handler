from __future__ import annotations

from functools import cache

from clingo import Function, Number
from clingo.symbol import Symbol, SymbolType

from flat_ch.core.domain import UserInput
from flat_ch.flattener import Flattener


def _tuple(items: list[Symbol]) -> Symbol:
    return Function("", items)


def _is_function(term: Symbol, name: str | None = None, arity: int | None = None) -> bool:
    if term.type != SymbolType.Function:
        return False
    if name is not None and term.name != name:
        return False
    if arity is not None and len(term.arguments) != arity:
        return False
    return True


@cache
def _flatten_legacy_tuple_cached(term: Symbol) -> tuple[Symbol, ...]:
    if not _is_function(term, ""):
        return (normalize_legacy_term(term),)

    args = term.arguments
    if len(args) == 0:
        return ()
    if len(args) == 2 and _is_function(args[1], ""):
        return (normalize_legacy_term(args[0]), *_flatten_legacy_tuple_cached(args[1]))

    return tuple(normalize_legacy_term(arg) for arg in args)


def flatten_legacy_tuple(term: Symbol) -> list[Symbol]:
    return list(_flatten_legacy_tuple_cached(term))


@cache
def _flatten_seq2_cached(term: Symbol) -> tuple[Symbol, ...]:
    if _is_function(term, "seq2", 2):
        left, right = term.arguments
        return (*_flatten_seq2_cached(left), *_flatten_seq2_cached(right))
    return (normalize_legacy_term(term),)


def flatten_seq2(term: Symbol) -> list[Symbol]:
    return list(_flatten_seq2_cached(term))


@cache
def normalize_legacy_term(term: Symbol) -> Symbol:
    if term.type != SymbolType.Function:
        return term

    args = term.arguments

    if term.name == "val" and len(args) == 2 and _is_function(args[0], "float", 0) and _is_function(args[1], "float", 1):
        return Function("val", [args[0], args[1].arguments[0]])

    if term.name == "operation":
        operator_symbol = normalize_legacy_term(args[0])
        argument_tuple = _tuple([]) if len(args) == 1 else _tuple(flatten_legacy_tuple(args[1]))
        return Function("operation", [operator_symbol, argument_tuple])

    if term.name == "seq2":
        return _tuple(flatten_seq2(term))

    if term.name == "statement_python":
        return Function("python", [normalize_legacy_term(arg) for arg in args])

    if term.name == "execution_input" and len(args) == 2:
        return _tuple([normalize_legacy_term(args[0]), normalize_legacy_term(args[1]), Function("in", [])])

    if term.name == "execution_output" and len(args) == 2:
        return _tuple([normalize_legacy_term(args[0]), normalize_legacy_term(args[1]), Function("out", [])])

    return Function(term.name, [normalize_legacy_term(arg) for arg in args])


@cache
def normalize_execution_declare(execution: Symbol) -> Symbol:
    args = execution.arguments
    if len(args) == 5:
        _, name_symbol, statements, inputs, outputs = args
    elif len(args) == 4:
        name_symbol, statements, inputs, outputs = args
    else:
        raise ValueError(f"Unsupported execution_declare arity: {len(args)}")

    return Function(
        "execution_declare",
        [
            normalize_legacy_term(name_symbol),
            _tuple(flatten_seq2(statements)),
            _tuple(flatten_legacy_tuple(inputs)),
            _tuple(flatten_legacy_tuple(outputs)),
        ],
    )


class CHFlattener(Flattener):
    def flatten(self, clingo_term):
        self.emitted_facts.clear()
        self._process_ch_declaration(clingo_term)
        return self.emitted_facts

    def _flatten_expression(self, clingo_term) -> int:
        return super()._flatten_expression(normalize_legacy_term(clingo_term))

    def _emit_current(self, node_type: UserInput, arguments: tuple[Symbol, ...]) -> None:
        self._process_declaration(node_type, node_type.value, arguments)

    def _process_ch_declaration(self, clingo_term: Symbol) -> None:
        term_name = clingo_term.name
        args = clingo_term.arguments

        if term_name == "variable_declare":
            self._handle_variable_declare(args)
            return

        if term_name == "variable_declareOptional" and len(args) == 1:
            identifier = normalize_legacy_term(args[0])
            self._emit_current(UserInput.DECLARE, (identifier,))
            self._emit_current(UserInput.DOMAIN, (identifier, self._none_value()))
            return

        if term_name == "variable_domain" and len(args) == 2:
            self._emit_current(UserInput.DOMAIN, (normalize_legacy_term(args[0]), args[1]))
            return

        if term_name == "variable_define":
            if len(args) == 2:
                self._emit_current(UserInput.DEFINE, (normalize_legacy_term(args[0]), args[1]))
                return
            if len(args) == 3:
                self._emit_current(UserInput.DEFINE, (normalize_legacy_term(args[1]), args[2]))
                return

        if term_name == "ensure":
            if len(args) == 1:
                self._emit_current(UserInput.ENSURE, (Function("__anonymous", []), args[0]))
                return
            if len(args) == 2:
                self._emit_current(UserInput.ENSURE, (normalize_legacy_term(args[0]), args[1]))
                return

        if term_name == "evaluate":
            if len(args) == 2:
                expr_id = self._flatten_expression(Function("operation", [args[0], args[1]]))
                self.emitted_facts.append(Function("evaluate", [args[0], args[1], Number(expr_id)]))
                return
            if len(args) == 3:
                expr_id = self._flatten_expression(Function("operation", [args[1], args[2]]))
                self.emitted_facts.append(Function("evaluate", [args[1], args[2], Number(expr_id)]))
                return

        if term_name == "bool_evaluate" and len(args) == 2:
            expr_id = self._flatten_expression(args[1])
            self.emitted_facts.append(Function("bool_evaluate", [args[1], Number(expr_id)]))
            return

        if term_name == "set_declare":
            if len(args) == 1:
                self._emit_current(UserInput.SET_DECLARE, (normalize_legacy_term(args[0]),))
                return
            if len(args) == 2:
                self._emit_current(UserInput.SET_DECLARE, (normalize_legacy_term(args[1]),))
                return

        if term_name == "set_baseDomain":
            if len(args) == 2:
                self._emit_current(UserInput.SET_BASE_DOMAIN, (normalize_legacy_term(args[0]), args[1]))
                return
            if len(args) == 3:
                self._emit_current(UserInput.SET_BASE_DOMAIN, (normalize_legacy_term(args[1]), args[2]))
                return

        if term_name == "set_assign":
            if len(args) == 2:
                self._emit_current(UserInput.SET_ASSIGN, (normalize_legacy_term(args[0]), args[1]))
                return
            if len(args) == 3:
                self._emit_current(UserInput.SET_ASSIGN, (normalize_legacy_term(args[1]), args[2]))
                return

        if term_name == "optimize_maximizeSum":
            if len(args) == 3:
                self._emit_current(UserInput.OPTIMIZE_SUM, (args[0], normalize_legacy_term(args[1]), normalize_legacy_term(args[2])))
                return
            if len(args) == 4:
                self._emit_current(UserInput.OPTIMIZE_SUM, (args[1], normalize_legacy_term(args[2]), normalize_legacy_term(args[3])))
                return

        if term_name == "optimize_precision":
            if len(args) == 1:
                self._emit_current(UserInput.OPTIMIZE_PRECISION, (args[0], Function("all", [])))
                return
            if len(args) == 2:
                self._emit_current(UserInput.OPTIMIZE_PRECISION, (args[0], normalize_legacy_term(args[1])))
                return

        raise ValueError(f"Unsupported CH declaration: {clingo_term}")

    def _handle_variable_declare(self, args: tuple[Symbol, ...]) -> None:
        if len(args) == 1:
            identifier = normalize_legacy_term(args[0])
            self._emit_current(UserInput.DECLARE, (identifier,))
            return

        if len(args) == 2:
            identifier = normalize_legacy_term(args[0])
            self._emit_current(UserInput.DECLARE, (identifier,))
            return

        if len(args) == 3:
            identifier = normalize_legacy_term(args[1])
            self._emit_current(UserInput.DECLARE, (identifier,))
            if _is_function(args[2], "boolDomain", 0):
                self._emit_current(UserInput.DOMAIN, (identifier, self._bool_value(True)))
                self._emit_current(UserInput.DOMAIN, (identifier, self._bool_value(False)))
            return

        raise ValueError(f"Unsupported variable_declare arity: {len(args)}")

    @staticmethod
    def _bool_value(value: bool) -> Symbol:
        return Function("val", [Function("bool", []), Function("true" if value else "false", [])])

    @staticmethod
    def _none_value() -> Symbol:
        return Function("val", [Function("none", []), Function("none", [])])