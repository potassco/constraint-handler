_tuple_aux(Tuple, N, ()) :- 
    _expression(compile2, Tuple),
    _expression_tupleLength(compile2, Tuple, N).
_tuple_aux(Tuple, N, (V, Tail)) :-
    _tuple_aux(Tuple, N+1, Tail),
    _expression_tupleIndex(compile2, Tuple, N, ARG),
    _se_domain(ARG, V).

_se_domain(Tuple, @pythonNestedToTuple(Values)) :-
    _tuple_aux(Tuple, 0, Values).

%%%%%%%%%%%%%%%%%% eq neq

_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, V),
   _se_domain(Expr2, V),
    true = @pythonIsTuple(V).


_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, V),
   not _se_domain(Expr2, V),
   not _se_domain(Expr2, bad),
   true = @pythonIsTuple(V).

_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr2, V),
   not _se_domain(Expr1, V),
   not _se_domain(Expr1, bad),
   true = @pythonIsTuple(V).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, V),
   not _se_domain(Expr2, V),
   not _se_domain(Expr2, bad),
   true = @pythonIsTuple(V).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr2, V),
   not _se_domain(Expr1, V),
   not _se_domain(Expr1, bad),
   true = @pythonIsTuple(V).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, V),
   _se_domain(Expr2, V),
    true = @pythonIsTuple(V).


:-
   not _se_value(Tuple, @pythonNestedToTuple(Values)),
   _tuple_aux(Tuple, 0, Values).

:-
   not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)),
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   _se_value(Expr2, V),
   true = @pythonIsTuple(V).

:-
   not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)),
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   not _se_value(Expr2, V),
   not _se_value(Expr2, bad),
   true = @pythonIsTuple(V).

:-
   not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)),
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, V),
   not _se_value(Expr1, V),
   not _se_value(Expr1, bad),
   true = @pythonIsTuple(V).

:-
   not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)),
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   not _se_value(Expr2, V),
   not _se_value(Expr2, bad),
   true = @pythonIsTuple(V).

:-
   not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)),
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, V),
   not _se_value(Expr1, V),
   not _se_value(Expr1, bad),
   true = @pythonIsTuple(V).

:-
   not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)),
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   _se_value(Expr2, V),
   true = @pythonIsTuple(V).