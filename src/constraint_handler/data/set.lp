#defined set_declare/2.
#defined set_assign/3.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).

_set_assign(CNAME,X,E) :- engine(CNAME,compile), set_assign(CNAME,X,E).
_set_declare(CNAME,X) :- engine(CNAME,compile), set_declare(CNAME,X).

direct_query(E)    :- _set_assign(NAME,X,E).
direct_query(EX)   :- _set_assign(NAME,X,E), EX=variable(X).

representation(set,intensional).

%%%%%%%%%%%%%%%%% length

computed(length,ARGS,val(int,N)) :- compute(length,ARGS),
    ARGS = (val(set,SET),()),
    N = #count { V,T : _set_contains(SET,T,V) }.

%%%%%%%%%%%%%%%%% set_declare set_assign set_value

%eValue(EX,set,EX) :- EX=variable(X), _set_declare(NAME,X).
eValue(EX,set,ER) :- EX=variable(X), ER=ref(variable(X)), _set_declare(NAME,X).
_set_contains(ER,T,V) :- representation(T,extensional), _set_assign(NAME,X,EV), eValue(variable(X),set,ER), eValue(EV,T,V).

compute(eq,(val(T,V1),(val(T,V2),()))) :- representation(T,intensional),
    _set_assign(N1,X,E1), eValue(E1,T,V1),
    _set_assign(N2,X,E2), eValue(E2,T,V2), V1 < V2.
_set_contains(ER,T,V1) :- representation(T,intensional),
    _set_assign(NAME,X,E1), eValue(E1,T,V1), eValue(variable(X),set,ER),
    #false : _set_assign(N2,X,E2), eValue(E2,T,V2), computed(eq,(val(T,V2),(val(T,V1),())),val(bool,true)), V2 < V1.

set_value(X,T,V) :- eValue(EV,set,E), _set_contains(E,T,V), EV=variable(X).

%%%%%%%%%%%%%%%%% isin notin

computed(isin,ARGS,val(bool,true))  :- compute(isin,ARGS), ARGS = (val(T,V),(val(set,S),())),
    representation(T,extensional),     _set_contains(S,T,V).
computed(isin,ARGS,val(bool,false)) :- compute(isin,ARGS), ARGS = (val(T,V),(val(set,S),())),
    representation(T,extensional), not _set_contains(S,T,V).
computed(notin,ARGS,val(bool,false)) :- compute(notin,ARGS), ARGS = (val(T,V),(val(set,S),())),
    representation(T,extensional),     _set_contains(S,T,V).
computed(notin,ARGS,val(bool,true))  :- compute(notin,ARGS), ARGS = (val(T,V),(val(set,S),())),
    representation(T,extensional), not _set_contains(S,T,V).

compute(eq,(val(T,V1),(val(T,V2),())))  :- compute((isin;notin),ARGS), ARGS = (val(T,V1),(val(set,S),())),
    representation(T,intensional), _set_contains(S,T,V2).

computed(isin,ARGS,val(bool,true))   :- compute(isin,ARGS), ARGS = (val(T,V1),(val(set,S),())),
    representation(T,intensional), _set_contains(S,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).
computed(isin,ARGS,val(bool,false))  :- compute(isin,ARGS), ARGS = (val(T,V1),(val(set,S),())),
    representation(T,intensional), #false : _set_contains(S,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).
computed(notin,ARGS,val(bool,false)) :- compute(isin,ARGS), ARGS = (val(T,V1),(val(set,S),())),
    representation(T,intensional), _set_contains(S,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).
computed(notin,ARGS,val(bool,true))  :- compute(isin,ARGS), ARGS = (val(T,V1),(val(set,S),())),
    representation(T,intensional), #false : _set_contains(S,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).

%%%%%%%%%%%%%%%%% makeSet

computed(makeSet,ARGS,val(set,ref(makeSet(ARGS)))) :- compute(makeSet,ARGS).
compute(eq,(val(T,V1),(val(T,V2),()))) :- compute(makeSet,ARGS),
    val(T,V1)=@pythonListElements(ARGS), val(T,V2)=@pythonListElements(ARGS),
    representation(T,intensional), V1 < V2.
_set_contains(ER,T,V) :- compute(makeSet,ARGS), computed(makeSet,ARGS,val(set,ER)),
    val(T,V)=@pythonListElements(ARGS), representation(T,extensional).
_set_contains(ER,T,V1) :- compute(makeSet,ARGS), computed(makeSet,ARGS,val(set,ER)), representation(T,intensional),
    val(T,V1)=@pythonListElements(ARGS),
    #false : val(T,V2)=@pythonListElements(ARGS), computed(eq,(val(T,V2),(val(T,V1),())),val(bool,true)), V2 < V1.

%%%%%%%%%%%%%%%%% filter
%%% TODO

%%%%%%%%%%%%%%%%%% add
%%% TODO

%%%%%%%%%%%%%%%%% union inter

compute(eq,(val(T,VSMALL),(val(T,VBIG),()))) :- compute((union;inter),ARGS), ARGS = (val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional), (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL < VBIG.

computed(union,ARGS,val(set,ref(union(ARGS)))) :- compute(union,ARGS), ARGS = (val(set,S1),(val(set,S2),())).
_set_contains(ER,T,V) :- compute(union,ARGS), computed(union,ARGS,val(set,ER)),
    ARGS = (val(set,S1),(val(set,S2),())),
    representation(T,extensional), _set_contains((S1;S2),T,V).

_set_contains(ER,T,VR) :- compute(union,ARGS), computed(union,ARGS,val(set,ER)),
    ARGS = (val(set,S1),(val(set,S2),())),
    representation(T,intensional),
    (SR,SO)=((S1,S2);(S2,S1)), _set_contains(SR,T,VR),
    #false : _set_contains(SO,T,VO), computed(eq,(val(T,VO),(val(T,VR),())),val(bool,true)), VO < VR.

computed(inter,ARGS,val(set,ref(inter(ARGS))))   :- compute(inter,ARGS), ARGS = (val(set,S1),(val(set,S2),())).
_set_contains(ER,T,V) :- compute(inter,ARGS), computed(inter,ARGS,val(set,ER)),
    ARGS = (val(set,S1),(val(set,S2),())),
    representation(T,extensional), _set_contains(S1,T,V), _set_contains(S2,T,V).

_set_contains(ER,T,V) :- compute(inter,ARGS), computed(inter,ARGS,val(set,ER)),
    ARGS = (val(set,S1),(val(set,S2),())),
    representation(T,intensional),
    _set_contains(S1,T,V), _set_contains(S2,T,V).
_set_contains(ER,T,V) :- compute(inter,ARGS), computed(inter,ARGS,val(set,ER)),
    ARGS = (val(set,S1),(val(set,S2),())),
    representation(T,intensional),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)),
    V=(V1;V2), V=V1 : V1 < V2; V=V2 : V2 < V1.

%%%%%%%%%%%%%%%%% Equality
compute(eq,ARGS) :- compute(neq,ARGS), ARGS = (set(T1,S1),(set(T2,S2),())), (T1;T2)=set.
computed(neq,ARGS,val(bool,NEQ)) :- computed(eq,ARGS,val(bool,EQ)), ARGS = (val(T1,S1),(val(T2,S2),())), (T1;T2)=set, (EQ,NEQ)=((true,false);(false,true)).

computed(eq,ARGS,val(bool,true))  :- compute(eq,ARGS),  ARGS = (val(set,S1),(val(set,S2),())), not computed(eq,ARGS,val(bool,false)).

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS),  ARGS = (val(set,S1),(val(T2,S2),())), T2 != set.
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS),  ARGS = (val(T1,S1),(val(set,S2),())), T1 != set.

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V), not _set_contains(S2,T,V), representation(T,extensional).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(val(set,S1),(val(set,S2),())),
    _set_contains(S2,T,V), not _set_contains(S1,T,V), representation(T,extensional).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V1), representation(T,intensional),
    #false : _set_contains(S2,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS=(val(set,S1),(val(set,S2),())),
    _set_contains(S2,T,V2), representation(T,intensional),
    #false : _set_contains(S1,T,V1), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).

compute(eq,(val(T,V1),(val(T,V2),()))) :- compute(eq,ARGS), ARGS=(val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional).

%%%%%%%%%%%%%%%%% Equality axioms

:- computed(eq,(val(set,X),(val(set,X),())),val(bool,false)). %%% reflexivity
:- computed(eq,(val(set,X),(val(set,Y),())),val(bool,true)),
   computed(eq,(val(set,Y),(val(set,X),())),val(bool,false)). %%% symmetry
:- computed(eq,(val(set,L1),(val(set,R1),())),val(bool,true)),
   computed(eq,(val(set,L2),(val(set,R2),())),val(bool,true)),
   computed(eq,(val(set,L3),(val(set,R3),())),val(bool,false)),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset

compute(eq,(val(T,V1),(val(T,V2),()))) :- compute(subset,ARGS), ARGS = (val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional).
computed(subset,ARGS,val(bool,false)) :- compute(subset,ARGS), ARGS = (val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V), representation(T,extensional), not _set_contains(S2,T,V).
computed(subset,ARGS,val(bool,false)) :- compute(subset,ARGS), ARGS = (val(set,S1),(val(set,S2),())),
    _set_contains(S1,T,V1), representation(T,intensional),
    #false : _set_contains(S2,T,V2), computed(eq,(val(T,V1),(val(T,V2),())),val(bool,true)).

computed(subset,ARGS,val(bool,true))  :- compute(subset,ARGS), ARGS = (val(set,S1),(val(set,S2),())),
    not computed(subset,ARGS,val(bool,false)).
computed(subset,ARGS,val(bool,false)) :- compute(subset,ARGS), ARGS = (val(T1,S1),(val(T2,S2),())),
    (T1;T2) != set, (T1;T2) = set.

%%%%%%%%%%%%%%%%%% Fold
%%% set_fold: a -> b -> b

_set_makeIndex(VM) :- compute(fold,ARGS), ARGS = (val(function,VO),(val(set,VM),(val(TACC,VACC),()))).
_set_foldStep(fold,ARGS,0,TACC,VACC) :- compute(fold,ARGS), ARGS = (val(function,VO),(val(set,VM),(val(TACC,VACC),()))).
compute(VO,SUBARGS) :- compute(fold,ARGS), ARGS = (val(function,VO),(val(set,VM),(val(TSTART,VSTART),()))),
    _set_index(VM,I,TI,VI), _set_foldStep(fold,ARGS,I,TB,VB),
    SUBARGS = (val(TI,VI),(val(TB,VB),())).
_set_foldStep(fold,ARGS,I+1,TN,NEXT) :- compute(fold,ARGS), ARGS = (val(function,VO),(val(set,VM),(val(TSTART,VSTART),()))),
    _set_foldStep(fold,ARGS,I,TB,VB), _set_index(VM,I,TI,VI),
    SUBARGS = (val(TI,VI),(val(TB,VB),())),
    computed(VO,SUBARGS,val(TN,NEXT)).
computed(fold,ARGS,val(TB,VB)) :- compute(fold,ARGS), ARGS = (val(function,VO),(val(set,VM),(val(TSTART,VSTART),()))),
    _set_foldStep(fold,ARGS,I,TB,VB),
    _set_lastIndex(VM,I).



_set_index(EM,0,TV,RV) :- _set_makeIndex(EM),
    _set_contains(EM,TV,RV),
    #false : _set_contains(EM,TV1,RV1), (TV1,RV1) < (TV,RV).

_set_index(EM,I+1,TV,RV) :- _set_index(EM,I,TV0,RV0),
    _set_contains(EM,TV,RV), (TV0,RV0) < (TV,RV),
    #false : _set_contains(EM,TV1,RV1), (TV0,RV0) < (TV1,RV1), (TV1,RV1) < (TV,RV).

_set_lastIndex(EM,I+1) :- _set_index(EM,I,TV,RV),
    #false : _set_contains(EM,TV1,RV1), (TV,RV) < (TV1,RV1).

_set_lastIndex(EM,0) :- _set_makeIndex(EM),
    #false : _set_contains(EM,TV,RV).

%%%%%%%%%%%%%%%%% _set_implode
%_set_implode(REF) :- _direct_implode(val(set,REF)).
%_set_implode(ref(REF)) :- _direct_implode(E), eValue(E,set,ref(REF)).
%_direct_imploded(E,V) :- _direct_implode(E), eValue(E,set,ref(REF)), _set_imploded(ref(REF),V).

_set_implode(REF) :- _direct_implode(val(set,REF)).
_set_implode(REF) :- _direct_implode(E), eValue(E,set,REF).
_direct_imploded(E,V) :- _direct_implode(E), E=val(set,REF), _set_imploded(REF,V).
_direct_imploded(E,V) :- _direct_implode(E), eValue(E,set,REF), _set_imploded(REF,V).

_direct_implode(val(TV,RV)) :- _set_implode(EM), _set_contains(EM,TV,RV).
_set_makeIndex(EM) :- _set_implode(EM).
_set_as_list_aux(EM,0,()) :- _set_implode(EM).
_set_as_list_aux(EM,IDX+1,K) :- _set_as_list_aux(EM,IDX,L), _set_index(EM,IDX,TV,RV), _direct_imploded(val(TV,RV),V), K=(V,L).
%_set_as_list_aux(EM,IDX+1,K) :- _set_as_list_aux(EM,IDX,L), _set_index(EM,IDX,TV,RV), K=(val(TV,RV),L). %% TODO, TV,RV should be imploded too
_set_imploded(EM,set(L)) :- _set_as_list_aux(EM,IDX,L), _set_lastIndex(EM,IDX).