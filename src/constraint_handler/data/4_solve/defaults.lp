#defined default_mode/1.

_default_possibleMode(basic;define;depends;none).
_default_modeProvided :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(MODE) :- default_mode(MODE), _default_possibleMode(MODE).
_default_mode(define) :- not _default_modeProvided.

%TODO: check if phases and labels matter

% Collect all subexpressions that occur in ensure statements.
_ensure_expression(E,E)  :- _passed(_,_,ensure(E)), _default_mode(depends).
_ensure_expression(E,D)  :- _ensure_expression(E, operation(_,ARGS)), D=@pythonListElements(ARGS).
_ensure_expression(E,D') :- _ensure_expression(E, D), true=@pythonIsTuple(D), D'=@pythonTupleElements(D).

_ensure_variable(E,X) :- _ensure_expression(E,variable(X)).

depends(X,X) :- _passed(_,_,variable_default(X,_,_)), _default_mode(depends).
depends(X,Y) :- _ensure_variable(E,X), _ensure_variable(E,Y), X != Y.

-apply(X,D,C) :- _passed(_,_,variable_default(X,D,C)), _passed(_,_,variable_define(X,E)),
                 _se_value(D,V), _se_value(E,V'), V != V',
                 _default_mode(define).

-apply(X,D,C) :- _passed(_,_,variable_default(X,D,C)),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(basic).

-apply(X,D,C) :- _passed(_,_,variable_default(X,D,C)), depends(X,X'), _passed(_,_,variable_define(X',_)),
                 _se_value(D,V), _se_value(variable(X),V'), V != V',
                 _default_mode(depends).

_se_value(variable(X),V) :- _passed(PHASE,LBL,variable_default(X,D,C)), _se_value(D,V), not -apply(X,D,C), _se_value(C,val(bool,true)).
