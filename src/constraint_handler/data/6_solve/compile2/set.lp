
_se_value(Expr, bad) :- _set_bad(Expr).

_bad_is_bad_set(set_make; union; inter; diff; subset; set_isin; set_notin).

_set_bad(operation(OP, ExprList)) :-
    _expression(compile2, operation(OP, ExprList)),
    _bad_is_bad_set(OP),
    _expression_operationIndex(compile2, operation(OP, ExprList), _, Arg),
    _se_value(Arg, bad).

_set_operation_has_bad_input(operation(OP, ExprList)) :-
    _expression(compile2, operation(OP, ExprList)),
    OP = (set_make; union; inter),
    _expression_operationIndex(compile2, operation(OP, ExprList), _, Arg),
    _se_value(Arg, bad).

_set_operation_has_bad_input(operation(diff, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    _se_value((Expr1;Expr2), bad).

_set_has_nonset_input(operation(OP, ExprList)) :-
    _expression(compile2, operation(OP, ExprList)),
    OP = (union; inter),
    _expression_operationIndex(compile2, operation(OP, ExprList), _, Expr),
    not _se_value(Expr, set).

_set_has_nonset_input(operation(diff, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set).

_set_has_nonset_input(operation(diff, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _se_value(Expr2, set).

%%%%%%%%%%%%%%%%% length
% bad if not set input
_set_bad(operation(length, (Expr, ()))) :-  _expression(compile2, operation(length, (Expr, ()))),
    not _se_value(Expr, set),
    not _type_dynamic(compile2,Expr,string). % weird
%% can be optimized using chaining if you know the domain
:-  _expression(compile2, operation(length, (Expr, ()))),
    not _set_bad(operation(length, (Expr, ()))),
    _se_value(Expr, set),
    N = #count { Val : _set_contains(Expr, Val) },
    not _se_value(operation(length, (Expr, ())), val(int, N)).

%%%%%%%%%%%%%%%%% set_isin set_notin
%%% we assume that none can be in the set

% bad if not set input
_set_bad(operation(set_isin, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    not _se_value(Expr2, set).
_set_bad(operation(set_notin, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    not _se_value(Expr2, set).


% true/false
:-  _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    not _set_bad(operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val),
    not _se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, true)).

:-  _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    not _set_bad(operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val),
    not _se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, false)).

%%% Abdallah: this operator should be removed as it can be easily expressed using set_isin and negation, and it complicates the implementation
:-  _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    not _set_bad(operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val),
    not _se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, true)).

:-  _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    not _set_bad(operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val),
    not _se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% set_make

_se_value(operation(set_make, ExprList), set) :-
    _expression(compile2, operation(set_make, ExprList)),
    not _set_operation_has_bad_input(operation(set_make, ExprList)).

_set_contains(operation(set_make, ExprList), Val) :-
    _expression(compile2, operation(set_make, ExprList)),
    not _set_bad(operation(set_make, ExprList)),
    _expression_operationIndex(compile2, operation(set_make, ExprList), _, Expr),
    _se_value(Expr, Val).

%%%%%%%%%%%%%%%%% union

% bad if not set input
_set_bad(operation(union, ExprList)):- _expression(compile2, operation(union, ExprList)),
    _expression_operationIndex(compile2, operation(union, ExprList), _, Expr),
    not _se_value(Expr, set).

_se_value(operation(union, ExprList), set) :-
    _expression(compile2, operation(union, ExprList)),
    not _set_has_nonset_input(operation(union, ExprList)),
    not _set_operation_has_bad_input(operation(union, ExprList)).

% derive membership from the arguments
_set_contains(operation(union, ExprList), Val) :-
    _expression(compile2, operation(union, ExprList)),
    not _set_bad(operation(union, ExprList)),
    _expression_operationIndex(compile2, operation(union, ExprList), _, Expr),
    _se_value(Expr, set),
    _set_contains(Expr, Val).

%%%%%%%%%%%%%%%%% inter

% bad if not set input
_set_bad(operation(inter, ExprList)):- _expression(compile2, operation(inter, ExprList)),
    _expression_operationIndex(compile2, operation(inter, ExprList), _, Expr),
    not _se_value(Expr, set).

_se_value(operation(inter, ExprList), set) :-
    _expression(compile2, operation(inter, ExprList)),
    not _set_has_nonset_input(operation(inter, ExprList)),
    not _set_operation_has_bad_input(operation(inter, ExprList)).

% derive membership from the arguments
_set_contains(operation(inter, (Expr1, Rest)), Val) :-
    _expression(compile2, operation(inter, (Expr1, Rest))),
    not _set_bad(operation(inter, (Expr1, Rest))),
    _set_contains(Expr1, Val),
    _set_contains(Expr, Val) : _expression_operationIndex(compile2, operation(inter, (Expr1, Rest)), Idx, Expr), Idx > 0.

%%%%%%%%%%%%%%%%% diff

% bad if not set input
_set_bad(operation(diff, (Expr1, (Expr2, ())))) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set).

_se_value(operation(diff, (Expr1, (Expr2, ()))), set) :-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _set_has_nonset_input(operation(diff, (Expr1, (Expr2, ())))) ,
    not _set_operation_has_bad_input(operation(diff, (Expr1, (Expr2, ())))) .
_set_bad(operation(diff, (Expr1, (Expr2, ())))) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _se_value(Expr2, set).

% derive membership from the arguments
_set_contains(operation(diff, (Expr1, (Expr2, ()))), Val) :-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _set_bad(operation(diff, (Expr1, (Expr2, ())))),
    _set_contains(Expr1, Val),
    not _set_contains(Expr2, Val).

%%%%%%%%%%%%%%%%% Equality

% false/true if not both are sets
_aux_eq_false(eq, val(bool, false)).
_aux_eq_false(neq, val(bool, true)).

_set_bad(operation(OP, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    OP=(eq;neq),
    _se_value((Expr1;Expr2), bad).

:- _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    not _set_bad(operation(OP, (Expr1, (Expr2, ())))),
    _aux_eq_false(OP, Val),
    _se_value(Expr1, set),
    not _se_value(Expr2, set),
    not _se_value(operation(OP, (Expr1, (Expr2, ()))), Val).

:- _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    not _set_bad(operation(OP, (Expr1, (Expr2, ())))),
    _aux_eq_false(OP, Val),
    not _se_value(Expr1, set),
    _se_value(Expr2, set),
    not _se_value(operation(OP, (Expr1, (Expr2, ()))), Val).

_neq_sets(Expr1, Expr2) :-
    _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _set_contains(Expr1, Val),
    not _set_contains(Expr2, Val).
_neq_sets(Expr1, Expr2) :-
    _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    not _set_contains(Expr1, Val),
    _set_contains(Expr2, Val).

:-  _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    not _set_bad(operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)).

:-  _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    not _set_bad(operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

%%% Abdallah: we do not need neq if we have not
:-  _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    not _set_bad(operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-  _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    not _set_bad(operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% Subset

% bad if not set input
_set_bad(operation(subset, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    not _se_value(Expr2, set).
_set_bad(operation(subset, (Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set).

_not_subset(Expr1, Expr2) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _set_contains(Expr1, Val),
    not _set_contains(Expr2, Val).

:-  _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    not _set_bad(operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    not _not_subset(Expr1, Expr2),
    not _se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, true)).

:-  _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    not _set_bad(operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _not_subset(Expr1, Expr2),
    not _se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%%% Fold
%%%%%%%%%%%%%%%%% _set_implode %% not fact format
