:- _python_evaluation(Expr, Uid),
   _se_value(ArgExpr, ArgVal) : _python_evaluation_input(Expr, Uid, ArgExpr, ArgVal), not _se_is_set(ArgExpr);
   _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(SetUid, pos, Value), _se_is_set(ArgExpr);
   not _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(SetUid, neg, Value), _se_is_set(ArgExpr);
   _python_evaluation_input_set_true(Expr, Uid, ArgExpr, SetUid) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_is_set(ArgExpr);
    _python_evaluation_output(Expr, Uid, OutputVal),
   not _python_error_output(OutputVal),
   not _se_is_set(Expr),
   not _se_value(Expr, OutputVal).

_set_contains(Expr, Value) :-
   _python_evaluation(Expr, Uid),
   _se_value(ArgExpr, ArgVal) : _python_evaluation_input(Expr, Uid, ArgExpr, ArgVal), not _se_is_set(ArgExpr);
   _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(SetUid, pos, Value), _se_is_set(ArgExpr);
   not _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(SetUid, neg, Value), _se_is_set(ArgExpr);
   _python_evaluation_input_set_true(Expr, Uid, ArgExpr, SetUid) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_is_set(ArgExpr);
    _python_evaluation_output(Expr, Uid, OutputVal),
   not _python_error_output(OutputVal),
   _se_is_set(Expr),
   _se_set_domain(OutputVal, pos, Value).

_python_error_output(error(Kind, Message)) :-
   _python_evaluation_output(_, _, error(Kind, Message)).

_warning(Kind, (), (python, Expr, Message)) :-
   _python_evaluation_output(Expr, Uid, error(Kind, Message)).


_python_evaluation_input_set_false(Expr, Uid, ArgExpr, SetUid) :-
   _python_evaluation_input(Expr, Uid, ArgExpr, SetUid),
   _se_is_set(ArgExpr),
   _se_set_domain(SetUid, neg, Value),
   _set_contains(ArgExpr, Value).

_python_evaluation_input_set_false(Expr, Uid, ArgExpr, SetUid) :-
   _python_evaluation_input(Expr, Uid, ArgExpr, SetUid),
   _se_is_set(ArgExpr),
   _se_set_domain(SetUid, pos, Value),
   not _set_contains(ArgExpr, Value).

_python_evaluation_input_set_true(Expr, Uid, ArgExpr, SetUid) :-
   _python_evaluation_input(Expr, Uid, ArgExpr, SetUid),
   _se_is_set(ArgExpr),
   not _python_evaluation_input_set_false(Expr, Uid, ArgExpr, SetUid).
