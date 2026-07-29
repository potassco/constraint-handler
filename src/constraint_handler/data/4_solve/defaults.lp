#defined default_mode/1.

_default_possibleMode(basic;define;depends;none).
_default_modeProvided :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(MODE) :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(define) :- not _default_modeProvided.

%TODO: rework phase integration and value introduction to be compatible with the propagator engine

_se_value(variable(X),V) :- _passed(solve,LBL,variable_default(X,D,C)), _se_value(D,V), not -apply(X,D,C), _se_value(C,val(bool,true)).

%%%%%% mode basic
-apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(basic).

%%%%%% mode define
-apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)), _passed(solve,LBL',variable_define(X,E)),
                 _se_value(D,V), _se_value(E,V'), V != V',
                 _default_mode(define).

%%%%%% mode depends
% Collect all variables that occur in ensure declarations.
_ensure_variable(E,X)  :- _passed(solve,LBL,ensure(E)), _default_mode(depends), X=@pythonExpressionVariable(E).

depends(X,X) :- _passed(solve,LBL,variable_default(X,D,C)), _default_mode(depends).
depends(X,Y) :- _ensure_variable(E,X), _ensure_variable(E,Y), X != Y.

-apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)), depends(X,X'), _passed(solve,LBL',variable_define(X',E')),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(depends).
