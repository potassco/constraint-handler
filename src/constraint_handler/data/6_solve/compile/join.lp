_join_element(X,E) :- _passed((compile;ground),LBL,variable_element(X,E,C)), _se_value(C,val(bool,true)), _passed((compile;ground),DECL_LBL,variable_declare(X,join,DECL_COND)), _se_value(DECL_COND,val(bool,true)).
_join_single(X,E) :- _join_element(X,E), 1 = #count { E2 : _join_element(X,E2) }.
_join_multiple(X) :- _join_element(X,E1), _join_element(X,E2), E1 != E2.
_join_value(X,bool,V) :- _join_element(X,E), _se_value(E,val(bool,V)).
_join_value(X,int,V) :- _join_element(X,E), _se_value(E,val(int,V)).
_join_value(X,float,V) :- _join_element(X,E), _se_value(E,val(float,V)).
_join_value(X,set,R) :- _join_element(X,E), _se_value(E,ref(set,R)).

_join_supported(E,V) :- _join_element(X,E), _se_value(E,V), V=val(T,_), T=(bool;int;float).
_join_supported(E,V) :- _join_element(X,E), _se_value(E,V), V=ref(set,_).

_join_bad(X) :- _join_element(X,E), _se_value(E,bad).
_join_bad(X) :- _join_multiple(X), _join_value(X,T,_), _join_value(X,U,_), T != U.
_join_bad(X) :- _join_multiple(X), _join_element(X,E), _se_value(E,V), V != bad, not _join_supported(E,V).
_join_bad(X) :- _join_element(X,E), not _se_value(E,_).
_join_bad(X) :- _passed((compile;ground),LBL,variable_declare(X,join,C)), _se_value(C,val(bool,true)), not _join_element(X,_).

_se_value(variable(X),V) :- _join_single(X,E), _se_value(E,V).
_se_value(variable(X),val(bool,true)) :- _join_value(X,bool,true), not _join_bad(X).
_se_value(variable(X),val(bool,false)) :- _join_value(X,bool,false), not _join_value(X,bool,true), not _join_bad(X).
_se_value(variable(X),val(int,V)) :- _join_value(X,int,V), not _join_bad(X), #false : _join_value(X,int,OTHER), OTHER > V.
_se_value(variable(X),val(float,V)) :- _join_value(X,float,V), not _join_bad(X), #false : _join_value(X,float,OTHER), @pythonFloatBinary(gt,OTHER,V)=val(bool,true).
_se_value(variable(X),ref(set,variable(X))) :- _join_multiple(X), _join_value(X,set,_), not _join_bad(X).
_set_candidate(variable(X),V) :- _join_multiple(X), _join_value(X,set,R), _set_contains(R,V), not _join_bad(X).
_se_value(variable(X),bad) :- _join_bad(X).