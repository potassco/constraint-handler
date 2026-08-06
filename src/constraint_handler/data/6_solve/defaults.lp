#defined default_mode/1.

_default_possibleMode(basic;define;depends;none).
_default_modeProvided :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(MODE) :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(define) :- not _default_modeProvided.

%TODO: rework phase integration and value introduction to be compatible with the propagator engine

_se_value(variable(X),V) :- _passed(solve,LBL,variable_default(X,D,C)), _se_value(D,V), not -_default_apply(X,D,C), _se_value(C,val(bool,true)).

%%%%%% mode basic
-_default_apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(basic).

%%%%%% mode define
-_default_apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)), _passed(solve,LBL',variable_define(X,E)),
                 _se_value(D,V), _se_value(E,V'), V != V',
                 _default_mode(define).

%%%%%% mode depends
% Collect all variables that occur in ensure declarations.
_default_ensureVariable(E,X) :- _passed(solve,LBL,ensure(E)), _default_mode(depends), X=@pythonExpressionVariable(E).
_default_dependVariable(E,X) :- _default_ensureVariable(E,X), _passed(solve,LBL,variable_default(X,D,C)).

_default_depends(X,X) :- _default_dependVariable(E,X).
_default_depends(X,Y) :- _default_dependVariable(E,X), _default_ensureVariable(E,Y), X != Y.

-_default_apply(X,D,C) :- _passed(solve,LBL,variable_default(X,D,C)), _passed(solve,LBL',variable_define(X',E')),
                 _default_depends(X,X'),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(depends).
