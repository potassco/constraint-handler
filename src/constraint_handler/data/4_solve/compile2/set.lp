%%% Abdallah: what to do about none, bad, and non set expressions


% set contains
{_set_contains(Set, Val)} :-
    _set_domain(Set, Expr),
    _se_value(Expr, Val),
    Val = val(_, _).

%%%%%%%%%%%%%%%%% length

%% can be optimized using chaining if you know the domain
_se_domain(operation(length, (Expr, ())), val(int, 0..Max)) :-
    _expression(compile2, operation(length, (Expr, ()))),
    _se_value(Expr, set),
    Max = #count { Val : _set_domain(Expr, _), _se_domain(Expr, Val) }.

%%%%%%%%%%%%%%%%% set_isin set_notin
%%% we assume that none can be in the set

_se_domain(operation(set_isin, (Expr1, (Expr2, ()))), (val(bool, true);val(bool, false))) :- 
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))).

%%% Abdallah: this operator should be removed as it can be easily expressed using set_isin and negation, and it complicates the implementation
_se_domain(operation(set_notin, (Expr1, (Expr2, ()))), (val(bool, true);val(bool, false))) :-
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))).

%%%%%%%%%%%%%%%%% set_make

_se_value(operation(set_make, ExprList), set) :- _expression(compile2, operation(set_make, ExprList)).

_member(ExprList,Expr) :- _expression(compile2, operation(set_make, ExprList)), Expr = @pythonListElements(ExprList).
_set_domain(operation(set_make, ExprList), Expr) :- 
    _expression(compile2, operation(set_make, ExprList)), _member(ExprList,Expr).
    
%%%%%%%%%%%%%%%%% union

_se_value(operation(union, ExprList), set) :- _expression(compile2, operation(union, ExprList)).
_se_domain(operation(union, ExprList), set) :- _expression(compile2, operation(union, ExprList)).

_member(ExprList,Expr) :- _expression(compile2, operation(union, ExprList)), Expr = @pythonListElements(ExprList).
_set_domain(operation(union, ExprList), Elem) :- 
    _expression(compile2, operation(union, ExprList)), _member(ExprList,Expr), _set_domain(Expr, Elem).

%%%%%%%%%%%%%%%%% inter

_se_value(operation(inter, ExprList), set) :- _expression(compile2, operation(inter, ExprList)).
_se_domain(operation(inter, ExprList), set) :- _expression(compile2, operation(inter, ExprList)).
_set_domain(operation(inter, (Expr1, Rest)), Elem) :- _expression(compile2, operation(inter, (Expr1, Rest))),
    _set_domain(Expr1, Elem).
    
%%%%%%%%%%%%%%%%% diff

_se_value(operation(diff, (Expr1, (Expr2, ()))), set) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))).
_se_domain(operation(diff, (Expr1, (Expr2, ()))), set) :- _expression(compile2, operation(diff, (Expr1, (Expr2, ())))).
_set_domain(operation(diff, (Expr1, (Expr2, ()))), Elem) :- 
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    _set_domain(Expr1, Elem).

%%%%%%%%%%%%%%%%% Equality

_se_domain(operation(eq, (Expr1, (Expr2, ()))), (val(bool, true);val(bool, false))) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))).

%%% Abdallah: we do not need neq if we have not
_se_domain(operation(neq, (Expr1, (Expr2, ()))), (val(bool, true);val(bool, false))) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))).

%%%%%%%%%%%%%%%%% Subset
_se_domain(operation(subset, (Expr1, (Expr2, ()))), (val(bool, true);val(bool, false))) :-
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))).

:-
    not _se_value(operation(length, (Expr, ())), val(int, N)),
    _expression(compile2, operation(length, (Expr, ()))),
    _se_value(Expr, set),
    N = #count { Val : _set_contains(Expr, Val) }.

:-
    not _se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val).

:-
    not _se_value(operation(set_isin, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(set_isin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val).

:-
    not _se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    not _set_contains(Expr2, Val).

:-
    not _se_value(operation(set_notin, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(set_notin, (Expr1, (Expr2, ())))),
    _se_value(Expr2, set),
    _se_value(Expr1, Val),
    _set_contains(Expr2, Val).

:-
    _expression(compile2, operation(set_make, ExprList)),
    _member(ExprList, Expr), _se_value(Expr, Val), 
    not _set_contains(operation(set_make, ExprList), Val).

:-
    _expression(compile2, operation(union, ExprList)),
    not _set_contains(operation(union, ExprList), Val),
    _member(ExprList, Expr), 
    _set_contains(Expr, Val).

:-
    _expression(compile2, operation(union, ExprList)),
    _set_contains(operation(union, ExprList), Val),
    not 1 {_set_contains(Expr, Val) : _member(ExprList, Expr)}.

:-
    _expression(compile2, operation(inter, ExprList)),
    _set_contains(operation(inter, ExprList), Val),
    #true : _member(ExprList, Expr), _set_contains(Expr, Val).

:-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    _set_contains(operation(diff, (Expr1, (Expr2, ()))), Val),
    _set_contains(Expr1, Val),
    _set_contains(Expr2, Val).

:-
    _expression(compile2, operation(diff, (Expr1, (Expr2, ())))),
    not _set_contains(operation(diff, (Expr1, (Expr2, ()))), Val),
    _set_contains(Expr1, Val),
    not _set_contains(Expr2, Val).

_neq_sets(Expr1, Expr2) :- 
    _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _set_contains(Expr1, Val), not _set_contains(Expr2, Val).
_neq_sets(Expr1, Expr2) :- 
    _expression(compile2, operation((eq;neq), (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _set_contains(Expr1, Val), _set_contains(Expr2, Val).

:-
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2).

:-
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2).

:-
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    not _se_value(Expr2, set).

:-
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set),
    _se_value(Expr2, set).

:-
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _neq_sets(Expr1, Expr2).

:-
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set),
    not _se_value(Expr2, set).

:-
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    not _se_value(Expr1, set),
    _se_value(Expr2, set).

:-
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _neq_sets(Expr1, Expr2).

_not_subset(Expr1, Expr2) :- 
     _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _set_contains(Expr1, Val), not _set_contains(Expr2, Val).

:-
    not _se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    not _not_subset(Expr1, Expr2).

:-
    not _se_value(operation(subset, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(subset, (Expr1, (Expr2, ())))),
    _se_value(Expr1, set), _se_value(Expr2, set),
    _not_subset(Expr1, Expr2).
