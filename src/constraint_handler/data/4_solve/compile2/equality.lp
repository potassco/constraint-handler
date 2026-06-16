%%%%%%%%%%%%%%%%% eq neq

_eq_comparable(Type) :- Type = (int;bool;symbol;string).

_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, val(Type, V)),
   _se_domain(Expr2, val(Type, V)),
    _eq_comparable(Type).

_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, val(Type, V)),
   not _se_domain(Expr2, val(Type, V)),
   not _se_domain(Expr2, bad),
   _eq_comparable(Type).

_se_domain(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
   _se_domain(Expr2, val(Type, V)),
   not _se_domain(Expr1, val(Type, V)),
   not _se_domain(Expr1, bad),
   _eq_comparable(Type).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, val(Type, V)),
   not _se_domain(Expr2, val(Type, V)),
   not _se_domain(Expr2, bad),
   _eq_comparable(Type).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr2, val(Type, V)),
   not _se_domain(Expr1, val(Type, V)),
   not _se_domain(Expr1, bad),
   _eq_comparable(Type).

_se_domain(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
   _se_domain(Expr1, val(Type, V)),
   _se_domain(Expr2, val(Type, V)),
   _eq_comparable(Type).