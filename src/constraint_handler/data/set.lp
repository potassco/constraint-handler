#defined set_declare/2.
#defined set_assign/3.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).
_set_assign(CNAME,variable(X),E) :- engine(CNAME,compile), set_assign(CNAME,X,E).
_set_declare(CNAME,variable(X)) :- engine(CNAME,compile), set_declare(CNAME,X).

direct_query(E)    :- _set_assign(NAME,X,E).

representation(set,intensional).

%%%%%%%%%%%%%%%%% length
operator_declare(OP,(T,()),int) :- T = set, OP = length.
computed(length,ARGS,val(int,N)) :- compute(length,ARGS),
    ARGS = (ref(set,SET),()),
    N = #count { V : _set_contains(SET,V) }.

%%%%%%%%%%%%%%%%% set_declare set_assign set_value

_se_value(EX,ref(set,EX)) :- _set_declare(NAME,EX).

compute(eq,(V1,(V2,()))) :-
    _set_assign(N1,EX,E1), _se_value(E1,V1),
    _set_assign(N2,EX,E2), _se_value(E2,V2), V1 < V2.
_set_contains(EX,V1) :-
    _set_assign(NAME,EX,E1), _se_value(E1,V1), %_se_value(EX,ref(set,ER)),
    #false : _set_assign(N2,EX,E2), _se_value(E2,V2), computed(eq,(V2,(V1,())),val(bool,true)), V2 < V1.

_set_assign(NAME,EX,S) :- _set_assign(NAME,EX,ER), ER=ref(set,S).

set_value(X,V) :- _se_value(EX,ref(set,E)), _set_contains(E,V), EX=variable(X).

%%%%%%%%%%%%%%%%% isin notin
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1),T2=set, OP = (isin;notin).
compute(eq,(V1,(V2,())))  :- compute((isin;notin),ARGS), ARGS = (V1,(ref(set,S),())),
    _set_contains(S,V2).

computed(isin,ARGS,val(bool,true))   :- compute(isin,ARGS), ARGS = (V1,(ref(set,S),())),
    _set_contains(S,V2), computed(eq,(V1,(V2,())),val(bool,true)).
computed(isin,ARGS,val(bool,false))  :- compute(isin,ARGS), ARGS = (V1,(ref(set,S),())),
    #false : _set_contains(S,V2), computed(eq,(V1,(V2,())),val(bool,true)).
computed(notin,ARGS,val(bool,false)) :- compute(notin,ARGS), ARGS = (V1,(ref(set,S),())),
    _set_contains(S,V2), computed(eq,(V1,(V2,())),val(bool,true)).
computed(notin,ARGS,val(bool,true))  :- compute(notin,ARGS), ARGS = (V1,(ref(set,S),())),
    #false : _set_contains(S,V2), computed(eq,(V1,(V2,())),val(bool,true)).

%%%%%%%%%%%%%%%%% makeSet
operator_declare_variadic(makeSet, T, set, 1) :- _type(T).
_set_declare(_internal,E) :- direct_query(E), E=operation(makeSet,L).
_set_assign(_internal,E,SE) :- direct_query(E), E=operation(makeSet,L), SE=@pythonListElements(L).

_set_declare(_internal,E) :- direct_query(E), E=set(L).
_set_assign(_internal,E,SE) :- direct_query(E), E=set(L), SE=@pythonListElements(L).

%%%%%%%%%%%%%%%%% filter
%%% TODO

%%%%%%%%%%%%%%%%%% add
%%% TODO

%%%%%%%%%%%%%%%%% union inter diff
operator_declare(OP,(T,(T,())),T) :- T = set, OP = (union;inter;diff).
_set_declare(_internal,E) :- direct_query(E), E=operation((diff;inter;union),L).
_set_assign(_internal,E,V) :- direct_query(E), E=operation(union,L), SE=@pythonListElements(L), _se_value(SE,ref(set,ER)), _set_contains(ER,V).

compute(eq,(VSMALL,(VBIG,()))) :- direct_query(E), E=operation((diff;inter),L), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,E,VSMALL) :- direct_query(E), E=operation(inter,L), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2), computed(eq,(VSMALL,(VBIG,())),val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,E,V1) :- direct_query(E), E=operation(diff,L), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    #false : _set_contains(R2,V2), computed(eq,(VSMALL,(VBIG,())),val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

%%%%%%%%%%%%%%%%% Equality
operator_declare(OP,(T,(T,())),bool) :- T = set, OP = (eq;neq).
compute(eq,ARGS) :- compute(neq,ARGS), ARGS = (set(T1,S1),(set(T2,S2),())), (T1;T2)=set.
computed(neq,ARGS,val(bool,NEQ)) :- computed(eq,ARGS,val(bool,EQ)), ARGS = (ref(T1,S1),(ref(T2,S2),())), (T1;T2)=set, (EQ,NEQ)=((true,false);(false,true)).

computed(eq,ARGS,val(bool,true))  :- compute(eq,ARGS),  ARGS = (ref(set,S1),(ref(set,S2),())), not computed(eq,ARGS,val(bool,false)).

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS),  ARGS = (ref(set,S1),(val(T2,S2),())), T2 != set.
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS),  ARGS = (val(T1,S1),(ref(set,S2),())), T1 != set.

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(ref(set,S1),(ref(set,S2),())),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), computed(eq,(V1,(V2,())),val(bool,true)).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(ref(set,S1),(ref(set,S2),())),
    _set_contains(S2,V2),
    #false : _set_contains(S1,V1), computed(eq,(V1,(V2,())),val(bool,true)).

compute(eq,(V1,(V2,()))) :- compute(eq,ARGS), ARGS=(ref(set,S1),(ref(set,S2),())),
    _set_contains(S1,V1), _set_contains(S2,V2).

%%%%%%%%%%%%%%%%% Equality axioms

:- computed(eq,(ref(set,X),(ref(set,X),())),val(bool,false)). %%% reflexivity
:- computed(eq,(ref(set,X),(ref(set,Y),())),val(bool,true)),
   computed(eq,(ref(set,Y),(ref(set,X),())),val(bool,false)). %%% symmetry
:- computed(eq,(ref(set,L1),(ref(set,R1),())),val(bool,true)),
   computed(eq,(ref(set,L2),(ref(set,R2),())),val(bool,true)),
   computed(eq,(ref(set,L3),(ref(set,R3),())),val(bool,false)),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset
operator_declare(OP,(T,(T,())),bool) :- T = (set), OP = subset.
compute(eq,(V1,(V2,()))) :- compute(subset,ARGS), ARGS = (ref(set,S1),(ref(set,S2),())),
    _set_contains(S1,V1), _set_contains(S2,V2).
computed(subset,ARGS,val(bool,false)) :- compute(subset,ARGS), ARGS = (ref(set,S1),(ref(set,S2),())),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), computed(eq,(V1,(V2,())),val(bool,true)).

computed(subset,ARGS,val(bool,true))  :- compute(subset,ARGS), ARGS = (ref(set,S1),(ref(set,S2),())),
    not computed(subset,ARGS,val(bool,false)).
computed(subset,ARGS,val(bool,false)) :- compute(subset,ARGS), ARGS = (val(T1,S1),(val(T2,S2),())),
    (T1;T2) != set, (T1;T2) = set.

%%%%%%%%%%%%%%%%%% Fold
%%% set_fold: a -> b -> b

_set_makeIndex(VM) :- compute(set_fold,ARGS), ARGS = (val(function,VO),(ref(set,VM),(ACC,()))).
_set_foldStep(set_fold,ARGS,0,ACC) :- compute(set_fold,ARGS), ARGS = (val(function,VO),(ref(set,VM),(ACC,()))).
compute(VO,SUBARGS) :- compute(set_fold,ARGS), ARGS = (val(function,VO),(ref(set,VM),(ACC,()))),
    _set_index(VM,I,VI), _set_foldStep(set_fold,ARGS,I,VB),
    SUBARGS = (VI,(VB,())).
_set_foldStep(set_fold,ARGS,I+1,NEXT) :- compute(set_fold,ARGS), ARGS = (val(function,VO),(ref(set,VM),(START,()))),
    _set_foldStep(set_fold,ARGS,I,VB), _set_index(VM,I,VI),
    SUBARGS = (VI,(VB,())),
    computed(VO,SUBARGS,NEXT).
computed(set_fold,ARGS,VB) :- compute(set_fold,ARGS), ARGS = (val(function,VO),(ref(set,VM),(START,()))),
    _set_foldStep(set_fold,ARGS,I,VB),
    _set_lastIndex(VM,I).



_set_index(EM,0,V) :- _set_makeIndex(EM),
    _set_contains(EM,V),
    #false : _set_contains(EM,V1), V1 < V.

_set_index(EM,I+1,V) :- _set_index(EM,I,V0),
    _set_contains(EM,V), V0 < V,
    #false : _set_contains(EM,V1), V0 < V1, V1 < V.

_set_lastIndex(EM,I+1) :- _set_index(EM,I,V),
    #false : _set_contains(EM,V1), V < V1.

_set_lastIndex(EM,0) :- _set_makeIndex(EM),
    #false : _set_contains(EM,V).

%%%%%%%%%%%%%%%%% _set_implode
_set_implode(REF) :- _direct_implode(ref(set,REF)).
_set_implode(REF) :- _direct_implode(E), _se_value(E,ref(set,REF)).
_direct_imploded(E,V) :- _direct_implode(E), E=ref(set,REF), _set_imploded(REF,V).
_direct_imploded(E,V) :- _direct_implode(E), _se_value(E,ref(set,REF)), _set_imploded(REF,V).

_direct_implode(val(TV,RV)) :- _set_implode(EM), _set_contains(EM,val(TV,RV)).
_set_makeIndex(EM) :- _set_implode(EM).
_set_as_list_aux(EM,0,()) :- _set_implode(EM).
_set_as_list_aux(EM,IDX+1,K) :- _set_as_list_aux(EM,IDX,L), _set_index(EM,IDX,val(TV,RV)), _direct_imploded(val(TV,RV),V), K=(V,L).
_set_imploded(EM,set(L)) :- _set_as_list_aux(EM,IDX,L), _set_lastIndex(EM,IDX).

%_direct_imploded(E,E) :- _direct_implode(E), E = set(_).
