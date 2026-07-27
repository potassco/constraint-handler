#const default_mode = define.

-apply(X,D,C) :- _passed(PHASE,LBL,variable_default(X,D,C)), _passed(PHASE,LBL,variable_define(X,E)), 
                 _se_value(D,V), _se_value(E,V'), V != V',
                 default_mode = define.
                 
-apply(X,D,C) :- _passed(PHASE,LBL,variable_default(X,D,C)), 
                 _se_value(D,V), _se_value(variable(X),V'), V != V', 
                 default_mode = basic.

_se_value(variable(X),V) :- _passed(PHASE,LBL,variable_default(X,D,C)), _se_value(D,V), not -apply(X,D,C), _se_value(C,val(bool,true)).