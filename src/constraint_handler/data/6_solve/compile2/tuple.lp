_tuple_value_index(Tuple, TupleValue, Idx, Value) :-
    _se_value(Tuple, TupleValue),
    _expression_tupleIndex(compile2, Tuple, Idx, _),
    (function, (), _, Args) = @pythonReify(TupleValue),
    (Idx, Value) = @pythonEnumerateElements(Args).

_tuple_set_component(Tuple, TupleValue, Idx, Arg, SetValue) :-
    _tuple_value_index(Tuple, TupleValue, Idx, SetValue),
    _expression_tupleIndex(compile2, Tuple, Idx, Arg),
    _se_is_set(Arg).

_se_set_domain_symbol(Arg, Uid, SetValue) :-
    _tuple_set_component(_, _, _, Arg, _),
    (Uid, SetValue) = @expression_set_domain_symbol(Arg). % convert from old weird format

_tuple_set_value_matches_uid(Arg, SetValue, Uid) :-
    _tuple_set_component(_, _, _, Arg, SetValue),
    _se_set_domain_symbol(Arg, Uid, SetValue).

:-
    _tuple_value_index(Tuple, TupleValue, Idx, Value),
    _expression_tupleIndex(compile2, Tuple, Idx, Arg),
    not _se_is_set(Arg),
    not _se_value(Arg, Value).

:-
    _tuple_value_index(Tuple, TupleValue, Idx, SetValue),
    _expression_tupleIndex(compile2, Tuple, Idx, Arg),
    _se_is_set(Arg),
    not _tuple_set_value_matches_uid(Arg, SetValue, _).

:-
    _tuple_value_index(Tuple, TupleValue, Idx, SetValue),
    _expression_tupleIndex(compile2, Tuple, Idx, Arg),
    _se_is_set(Arg),
    _tuple_set_value_matches_uid(Arg, SetValue, Uid),
    _se_set_domain(Uid, pos, Value),
    not _set_contains(Arg, Value).

:-
    _tuple_value_index(Tuple, TupleValue, Idx, SetValue),
    _expression_tupleIndex(compile2, Tuple, Idx, Arg),
    _se_is_set(Arg),
    _tuple_set_value_matches_uid(Arg, SetValue, Uid),
    _se_set_domain(Uid, neg, Value),
    _set_contains(Arg, Value).

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
