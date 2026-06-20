:- _python_evaluation(Expr, Uid),
   _se_value(ArgExpr, ArgVal) : _python_evaluation_input(Expr, Uid, ArgExpr, ArgVal), not _se_is_set(ArgExpr);
   _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, pos, Value), _se_is_set(ArgExpr);
   not _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, neg, Value), _se_is_set(ArgExpr);
    _python_evaluation_output(Expr, Uid, OutputVal),
   not _se_is_set(Expr),
   not _se_value(Expr, OutputVal).

_set_contains(Expr, Value) :-
   _python_evaluation(Expr, Uid),
   _se_value(ArgExpr, ArgVal) : _python_evaluation_input(Expr, Uid, ArgExpr, ArgVal), not _se_is_set(ArgExpr);
   _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, pos, Value), _se_is_set(ArgExpr);
   not _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, neg, Value), _se_is_set(ArgExpr);
    _python_evaluation_output(Expr, Uid, OutputVal),
   _se_is_set(Expr),
   _se_set_domain(Expr, OutputVal, pos, Value).

% :- _python_evaluation(Expr, Uid),
%    _se_value(ArgExpr, ArgVal) : _python_evaluation_input(Expr, Uid, ArgExpr, ArgVal), not _se_is_set(ArgExpr);
%    _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, pos, Value), _se_is_set(ArgExpr);
%    not _set_contains(ArgExpr, Value) : _python_evaluation_input(Expr, Uid, ArgExpr, SetUid), _se_set_domain(ArgExpr, SetUid, neg, Value), _se_is_set(ArgExpr);
%     _python_evaluation_output(Expr, Uid, OutputVal),
%    _se_is_set(Expr),
%    _set_contains(Expr, Value) : _se_set_domain(Expr, OutputVal, neg, Value).

% %%% selecting a precomputed python evaluation
% _python_evaluation_input_mismatch(PyExpr, Uid) :-
%     _python_evaluation_input(PyExpr, Uid, ArgExpr, ArgVal),
%     not _se_is_set(ArgExpr),
%     not _se_value(ArgExpr, ArgVal).

% _python_evaluation_input_mismatch(PyExpr, Uid) :-
%     _python_evaluation_input(PyExpr, Uid, ArgExpr, SetUid),
%     _se_is_set(ArgExpr),
%     not _se_chosen_set_domain(ArgExpr, SetUid).

% _python_selected_evaluation(PyExpr, Uid) :-
%     _python_evaluation(PyExpr, Uid),
%     not _python_evaluation_input_mismatch(PyExpr, Uid).

% :- _python_evaluation(Expr, _),
%    not _python_selected_evaluation(Expr, _).

% % :- _python_selected_evaluation(Expr, Uid1),
% %    _python_selected_evaluation(Expr, Uid2),
% %    Uid1 != Uid2.

% %%% non-error outputs
% :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, val(Type, Value)),
%     not _se_value(Expr, val(Type, Value)).

% %%% non-error set outputs
% :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, SetUid),
%     _se_set_domain(Expr, SetUid),
%     not _se_value(Expr, set).

% _set_contains(Expr, Arg) :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, SetUid),
%     _se_set_domain(Expr, SetUid),
%     _se_set_domain(Expr, SetUid, Arg).

% %%% explicit bad outputs
% :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, bad),
%     not _se_value(Expr, bad).

% %%% error outputs
% :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, error(Kind, Message)),
%     not _se_value(Expr, bad).

% %%% warnings on error
% _warning(Kind, (), (python, Expr, Message)) :-
%     _python_selected_evaluation(PyExpr, Uid),
%     _python_evaluation_output(PyExpr, Uid, error(Kind, Message)).
