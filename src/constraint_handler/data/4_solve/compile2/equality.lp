%%%%%%%%%%%%%%%%% eq neq

_eq_comparable(Type) :- Type = (int;bool;none;symbol;string;tuple).


:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr1, val(Type, V)),
   _se_value(Expr2, val(Type, V)),
    _eq_comparable(Type),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr1, val(Type, V)),
   not _se_value(Expr2, val(Type, V)),
   not _se_value(Expr2, bad),
   _eq_comparable(Type),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr2, val(Type, V)),
   not _se_value(Expr1, val(Type, V)),
   not _se_value(Expr1, bad),
   _eq_comparable(Type),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr1, val(Type, V)),
   not _se_value(Expr2, val(Type, V)),
   not _se_value(Expr2, bad),
   _eq_comparable(Type),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr2, val(Type, V)),
   not _se_value(Expr1, val(Type, V)),
   not _se_value(Expr1, bad),
   _eq_comparable(Type),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   not _float_operation((Expr1, (Expr2, ()))),
   not _se_value(Expr1, set),
   not _se_value(Expr2, set),
   _se_value(Expr1, val(Type, V)),
   _se_value(Expr2, val(Type, V)),
   _eq_comparable(Type),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)).
