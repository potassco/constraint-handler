_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=bool_evaluate(E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=ensure(E).
_top_level_expression(operation(OP,ARGS)) :- _passed(compile2,LBL,DECL), DECL=evaluate(OP,ARGS).

_top_level_expression(E;PREC) :- _passed(compile2,LBL,DECL), DECL=optimize_component(E,PREC,X,P).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=preference_holds(E,K).

_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=set_assign(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=set_baseDomain(X,E).
_top_level_expression(operation(set_make,())) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).

_top_level_expression(variable_define(X,E)) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(variable_domain(X,E)) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(set_assign(X,E)) :- _passed(compile2,LBL,DECL), DECL=set_assign(X,E).
_top_level_expression(set_baseDomain(X,E)) :- _passed(compile2,LBL,DECL), DECL=set_baseDomain(X,E).
_top_level_expression(set_baseDomain(X,operation(set_make,()))) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).

_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).

%%% load everything into python
_load_top_level_expressions :- _ = @load_top_level_expression(E), _top_level_expression(E).
_load_solver_identifiers :- _ = @load_solver_identifiers(ID), _main_solverIdentifiers(ID).
_loaded :- _load_top_level_expressions, _load_solver_identifiers.

%%% compute the domain of all subexpressions
%%% _se_domain(Expr, Value) means that Value is a possible value of Expr
%%% Value can either a real value like val(int, 5) or val(bad) or val(none, none)
%%% _se_is_set(Expr) means that Expr is a set-valued expression
%%% for such an expression we might have
%%% _se_set_domain_symbol()
%%% _se_set_domain(Expr, Uid) means that Uid is an identifier of a possible value of the set
%%% _se_set_domain(Uid, Sign, Value) means that Value is member of that Uid domain if Sign==pos
%%% _se_set_domain(Uid, Sign, Value) means that Value is not member of that Uid domain if Sign==neg

_se_domain(Expr, Value) :- (Expr, Value) = @expression_domain(), _loaded.
_se_set_domain(Expr, Uid) :- (Expr, Uid) = @expression_set_domain(), _loaded.
_se_set_domain(Uid, Sign, Value) :- (Uid, Sign, Value) = @expression_set_domain_value(), _loaded.
_se_is_set(Expr) :- Expr = @expression_set(), _loaded.

%%% compute the python evaluation traces
%%% _python_evaluation(Expr, Uid) means that Expr is a python expression and Uid is an identifier of one evaluation trace
%%% _python_evaluation_input(PyExpr, Uid, ArgExpr, ArgVal) means that the evaluation trace Uid of PyExpr included the the ArgExpr=ArgVal
%%% if _se_is_set(ArgExpr) then ArgVal is a Uid of the set domain, otherwise it is a concrete value
%%% _python_evaluation_output(PyExpr, Uid, OutputVal) means that the evaluation trace Uid of PyExpr produced OutputVal
%%% if _se_is_set(PyExpr) then OutputVal is a Uid of the set domain, otherwise it is a concrete value
_python_evaluation(Expr, Uid) :- (Expr, Uid) = @python_evaluation(), _loaded.
_python_evaluation_input(PyExpr, Uid, ArgExpr, ArgVal) :-
    (PyExpr, Uid, ArgExpr, ArgVal) = @python_evaluation_input(),
    _loaded.
_python_evaluation_output(PyExpr, Uid, OutputVal) :-
    (PyExpr, Uid, OutputVal) = @python_evaluation_output(),
    _loaded.

#script(python)

import clingo
from functools import cache

from constraint_handler.utils.python_domain_computation import ComputedDomains, DomainComputation


top_level_expressions: set[clingo.Symbol] = set()
solver_identifiers: list[clingo.Symbol] = []


@cache
def _computed_domains() -> ComputedDomains:
    """Compute and cache all expression domains and derived set metadata."""
    return DomainComputation.compute(tuple(sorted(top_level_expressions)), tuple(solver_identifiers))


def load_top_level_expression(cl_expr: clingo.Symbol) -> clingo.Symbol:
    top_level_expressions.add(cl_expr)
    return clingo.symbol.Infimum


def load_solver_identifiers(cl_id: clingo.Symbol) -> clingo.Symbol:
    solver_identifiers.extend(DomainComputation.normalize_solver_identifiers((cl_id,)))
    return clingo.symbol.Infimum


def expression_domain():
    computed = _computed_domains()
    return computed.expression_domain_symbols()


def expression_set_domain():
    computed = _computed_domains()
    return computed.expression_set_domain_symbols()


def expression_set_domain_value():
    computed = _computed_domains()
    return computed.expression_set_domain_value_symbols()


def expression_set_domain_symbol(cl_expr: clingo.Symbol):
    """Expose concrete set values only for the requested set-valued expression."""
    computed = _computed_domains()
    return computed.expression_set_domain_symbol_symbols(cl_expr)


def expression_set():
    computed = _computed_domains()
    return computed.set_expression_symbols()


def python_evaluation():
    computed = _computed_domains()
    return computed.python_evaluation_symbols()


def python_evaluation_input():
    computed = _computed_domains()
    return computed.python_evaluation_input_symbols()


def python_evaluation_output():
    computed = _computed_domains()
    return computed.python_evaluation_output_symbols()

#end.
