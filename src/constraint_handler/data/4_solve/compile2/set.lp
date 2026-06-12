%%% Abdallah: what to do about none, bad, and non set expressions

%%%%%%%%%%%%%%%%% length

%% can be optimized using chaining if you know the domain
_se_value(operation(length, (Expr, ())), val(int, N)) :-
    _expression(compile2, operation(length, (Expr, ()))),
    _se_value(Expr, set),
    N = #count { Val : _set_contains(Expr, Val) }.

%%%%%%%%%%%%%%%%% set_isin set_notin
%%% we assume that none can be in the set

_se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val).

_se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val).

%%% Abdallah: this operator should be removed as it can be easily expressed using set_isin and negation, and it complicates the implementation
_se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val).

_se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val).

%%%%%%%%%%%%%%%%% set_make

_se_value(operation(set_make, ExprList), set) :- _expression(compile2, operation(set_make, ExprList)).

_set_contains(operation(set_make, ExprList), Val) :-
    _expression(compile2, operation(set_make, ExprList)),
    Expr = @pythonListElements(ExprList),
    _se_value(Expr, Val).
    
%%%%%%%%%%%%%%%%% union

_se_value(operation(union, ExprList), set) :- _expression(compile2, operation(union, ExprList)).
_set_contains(operation(union, ExprList), Val) :- _expression(compile2, operation(union, ExprList)),
    Expr = @pythonListElements(ExprList),
    _se_value(Expr, set),
    _set_contains(Expr, Val).

%%%%%%%%%%%%%%%%% inter

_se_value(operation(inter, ExprList), set) :- _expression(compile2, operation(inter, ExprList)).
_set_contains(operation(inter, (Expr1, Rest)), Val) :- _expression(compile2, operation(inter, (Expr1, Rest))),
    _se_value(Expr1, set),
    _set_contains(Expr1, Val),
    _set_contains(Expr, Val) : Expr = @pythonListElements(Rest).
    
%%%%%%%%%%%%%%%%% diff

_se_value(operation(diff, (Expr1, (Expr2, ()))), set) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set).
_set_contains(operation(diff, (Expr1, (Expr2, ()))), Val) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    _se_value(Expr2, set),
    _set_contains(Expr1, Val),
    not _set_contains(Expr2, Val).

%%%%%%%%%%%%%%%%% Equality

_neq_sets(Expr1, Expr2) :- _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _set_contains(Expr1, Val), not _set_contains(Expr2, Val).
_neq_sets(Expr1, Expr2) :- _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _set_contains(Expr1, Val), _set_contains(Expr2, Val).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2).

%%% Abdallah: I guess this would be a type mismatch that should trigger bad and not false?
%%% but the tests require false
_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    not _se_value(Expr2, set).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set),
    _se_value(Expr2, set).

%%% Abdallah: we do not need neq if we have not
_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    not _se_value(Expr2, set).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set),
    _se_value(Expr2, set).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2).

%%%%%%%%%%%%%%%%% Subset

_not_subset(Expr1, Expr2) :- _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _set_contains(Expr1, Val), not _set_contains(Expr2, Val).

_se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _not_subset(Expr1, Expr2).

_se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _not_subset(Expr1, Expr2).

%%%%%%%%%%%%%%%%%% Fold
%%%%%%%%%%%%%%%%% _set_implode %% not fact format