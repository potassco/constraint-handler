_meet_element(X,E) :- _passed((compile;ground),LBL,variable_element(X,E,C)), _se_value(C,val(bool,true)), _passed((compile;ground),DECL_LBL,variable_declare(X,meet,DECL_COND)), _se_value(DECL_COND,val(bool,true)).
_meet_single(X,E) :- _meet_element(X,E), 1 = #count { E2 : _meet_element(X,E2) }.
_meet_multiple(X) :- _meet_element(X,E1), _meet_element(X,E2), E1 != E2.
_meet_value(X,bool,V) :- _meet_element(X,E), _se_value(E,val(bool,V)).
_meet_value(X,int,V) :- _meet_element(X,E), _se_value(E,val(int,V)).
_meet_value(X,float,V) :- _meet_element(X,E), _se_value(E,val(float,V)).
_meet_value(X,set,R) :- _meet_element(X,E), _se_value(E,ref(set,R)).

_meet_supported(E,V) :- _meet_element(X,E), _se_value(E,V), V=val(T,_), T=(bool;int;float).
_meet_supported(E,V) :- _meet_element(X,E), _se_value(E,V), V=ref(set,_).

_meet_bad(X) :- _meet_element(X,E), _se_value(E,bad).
_meet_bad(X) :- _meet_multiple(X), _meet_value(X,T,_), _meet_value(X,U,_), T != U.
_meet_bad(X) :- _meet_multiple(X), _meet_element(X,E), _se_value(E,V), V != bad, not _meet_supported(E,V).
_meet_bad(X) :- _meet_element(X,E), not _se_value(E,_).
_meet_bad(X) :- _passed((compile;ground),LBL,variable_declare(X,meet,C)), _se_value(C,val(bool,true)), not _meet_element(X,_).

_se_value(variable(X),V) :- _meet_single(X,E), _se_value(E,V).
_se_value(variable(X),val(bool,false)) :- _meet_value(X,bool,false), not _meet_bad(X).
_se_value(variable(X),val(bool,true)) :- _meet_value(X,bool,true), not _meet_value(X,bool,false), not _meet_bad(X).
_se_value(variable(X),val(int,V)) :- _meet_value(X,int,V), not _meet_bad(X), #false : _meet_value(X,int,OTHER), OTHER < V.
_se_value(variable(X),val(float,V)) :- _meet_value(X,float,V), not _meet_bad(X), #false : _meet_value(X,float,OTHER), @pythonFloatBinary(gt,V,OTHER)=val(bool,true).
_se_value(variable(X),ref(set,variable(X))) :- _meet_multiple(X), _meet_value(X,set,_), not _meet_bad(X).
_set_candidate(variable(X),V) :- _meet_multiple(X), _meet_value(X,set,R), _set_contains(R,V), not _meet_bad(X), #false : _meet_value(X,set,OTHER), not _set_contains(OTHER,V).
_se_value(variable(X),bad) :- _meet_bad(X).