%%%%%%%%%%%%%%%%% eq neq
_type_extensionalEquality(bool).

%%%%%%%%%%%%%%%%% lnot, snot, wnot
_computedIdx(E,val(bool,true))  :- _computeIdx(E,(lnot;snot;wnot)), _computeIdx(E,0,val(bool,false)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,(lnot;snot;wnot)), _computeIdx(E,0,val(bool,true)).

%% logical/classical negation
_computedIdx(E,val(none,none)) :- _computeIdx(E,lnot), _computeIdx(E,0,val(none,none)).

%% strong negation / strict negation
_se_value(operation(snot,(E1,())),val(bool,false)) :- direct_query(operation(snot,(E1,()))), _se_value(E1,val(none,none)).

%% weak negation / negation as weak failure
_se_value(operation(wnot,(E1,())),val(bool,true))  :- direct_query(operation(wnot,(E1,()))), _se_value(E1,val(none,none)).

%%%%%%%%%%%%%%%%% conj disj limp
%% The _compute/_computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation
_computedIdx(E,val(bool,false)) :- _computeIdx(E,conj), _computeIdx(E,IDX,val(bool,false)).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,conj), #false : _computeIdx(E,IDX,V), V!=val(bool,true).
_computedIdx(E,bad) :- _computeIdx(E,conj), _computeIdx(E,IDX,bad), #false : _computeIdx(E,JDX,val(bool,false)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,disj), _computeIdx(E,IDX,val(bool,true)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,disj), #false : _computeIdx(E,IDX,(val(bool,true);bad)).
_computedIdx(E,bad) :- _computeIdx(E,disj), _computeIdx(E,IDX,bad), #false : _computeIdx(E,JDX,val(bool,true)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,limp), _computeIdx(E,0,val(bool,false)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,limp), _computeIdx(E,1,val(bool,true)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,limp), _computeIdx(E,0,val(bool,true)), _computeIdx(E,1,val(bool,false)).

_computedIdx(E,val(none,none)) :- _computeIdx(E,limp), _computeIdx(E,0,val(bool,true)), _computeIdx(E,1,val(none,none)).
_computedIdx(E,val(none,none)) :- _computeIdx(E,limp), _computeIdx(E,0,val(none,none)), _computeIdx(E,1,val(bool,false)).
_computedIdx(E,val(none,none)) :- _computeIdx(E,limp), _computeIdx(E,0,val(none,none)), _computeIdx(E,1,val(none,none)).

_computedIdx(E,bad) :- _computeIdx(E,limp), _computeIdx(E,0,val(bool,true)), _computeIdx(E,1,bad).
_computedIdx(E,bad) :- _computeIdx(E,limp), _computeIdx(E,0,bad), _computeIdx(E,1,val(bool,V)), V!=true.

%%%%%%%%%%%%%%%%% lxor leqv
_computedIdx(E,val(bool,true)) :- _computeIdx(E,lxor),
    N = #count { IDX : _computeIdx(E,IDX,val(bool,true)) }, N \ 2 = 1.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, lxor),
    N = #count { IDX : _computeIdx(E,IDX,val(bool,true)) }, N \ 2 = 0.

_computedIdx(E,val(bool,true)) :- _computeIdx(E,leqv),
    N = #count { IDX : _computeIdx(E,IDX,val(bool,false)) }, N \ 2 = 0.
_computedIdx(E,val(bool,false)) :- _computeIdx(E,leqv),
    N = #count { IDX : _computeIdx(E,IDX,val(bool,false)) }, N \ 2 = 1.
