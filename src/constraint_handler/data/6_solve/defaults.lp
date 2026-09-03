#defined default_mode/1.

_default_possibleMode(basic;define;depends;none).
_default_modeProvided :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(MODE) :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(define) :- not _default_modeProvided.

%TODO: rework phase integration and value introduction to be compatible with the propagator engine


-_default_apply(X,D,C,P) :- _passed(solve,LBL,variable_default(X,D,C,P)),
  _se_value(C,val(bool,false)).

-_default_apply(X,D,C,P) :- _passed(solve,LBL,variable_default(X,D,C,P)), _default_apply(X,D',C',P'), D != D', P<=P'.
_default_apply(X,D,C,P) :- _passed(solve,LBL,variable_default(X,D,C,P)), not -_default_apply(X,D,C,P).

%%%%%% mode basic
-_default_apply(X,D,C,P) :- _passed(solve,LBL,variable_default(X,D,C,P)),
  _se_value(D,V), _se_value(variable(X),V'), V != V',
  _default_mode(basic).

%%%%%% mode define

-_default_apply(X,D,C,P) :- _passed(solve,LBL,variable_default(X,D,C,P)), _passed(solve,LBL2,variable_assign(X,E)),
  _default_mode(define).


%%%%%% mode depends
% Collect all variables that occur in ensure declarations.
_default_ensureVariable(E,X) :- _passed(solve,LBL,ensure(E)), _default_mode(depends), X=@pythonExpressionVariable(E).
_default_dependVariable(E,X) :- _default_ensureVariable(E,X), _passed(solve,LBL,variable_declare(X,open)).

_default_connect(X,Y) :- _default_dependVariable(E,X), _default_ensureVariable(E,Y), X != Y.
_default_connect(X,X) :- _passed(solve,LBL,variable_declare(X,open)).

-_default_apply(X,D,C,P) :-
  _passed(solve,LBL,variable_default(X,D,C,P)),
  _passed(solve,LBL2,variable_assign(Y,E)),
  _default_connect(X,Y),
  _default_mode(depends).


%%%%%% guessing
_se_value(variable(X),V) :- _passed((compile;compile2;ground),LBL,variable_assign(X,E)), _se_value(E,V).

_se_value(variable(X),V) :- _passed((compile;compile2;ground),LBL,variable_default(X,E,C,P)), _se_value(E,V), not -_default_apply(X,E,C,P).

0 { _se_value(variable(X),V) : _passed(solve,LBL1,variable_domain(X,E)), _se_value(E,V) } 1 :-
  _passed((compile;compile2;ground),LBL,variable_declare(X,open)).

:- _passed((compile;compile2;ground),LBL,variable_declare(X,open)), 1 != { _se_value(variable(X),V) }. % TODO change 1 != to 1 >
