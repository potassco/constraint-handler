_tuple_aux(Tuple, N, ()) :-
    _expression(compile2, Tuple),
    _expression_tupleLength(compile2, Tuple, N).
_tuple_aux(Tuple, N, (V, Tail)) :-
    _tuple_aux(Tuple, N+1, Tail),
    _expression_tupleIndex(compile2, Tuple, N, ARG),
    _se_value(ARG, V).

_python_argument_tuple(Tuple) :-
    _expression_operationIndex(compile2, operation(python(_), _), _, Tuple).

_python_argument_tuple(Tuple) :-
    _expression_operationIndex(compile2, operation(pythonExtract(_, _), _), _, Tuple).

_python_argument_tuple(Tuple) :-
    _expression_tupleIndex(compile2, Parent, _, Tuple),
    _python_argument_tuple(Parent).

:-
    _tuple_aux(Tuple, 0, Values),
    not _python_argument_tuple(Tuple),
    not _se_value(Tuple, @pythonNestedToTuple(Values)).

%%%%%%%%%%%%%%%%%% eq neq

:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   _se_value(Expr2, V),
    true = @pythonIsTuple(V),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)).


:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   not _se_value(Expr2, V),
   not _se_value(Expr2, bad),
   true = @pythonIsTuple(V),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, V),
   not _se_value(Expr1, V),
   not _se_value(Expr1, bad),
   true = @pythonIsTuple(V),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   not _se_value(Expr2, V),
   not _se_value(Expr2, bad),
   true = @pythonIsTuple(V),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, V),
   not _se_value(Expr1, V),
   not _se_value(Expr1, bad),
   true = @pythonIsTuple(V),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, V),
   _se_value(Expr2, V),
    true = @pythonIsTuple(V),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)).
