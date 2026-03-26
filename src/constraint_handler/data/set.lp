#defined set_declare/2.
#defined set_assign/3.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).
_set_assign(CNAME,variable(X),E) :- engine(CNAME,compile), set_assign(CNAME,X,E).
_set_declare(CNAME,variable(X)) :- engine(CNAME,compile), set_declare(CNAME,X).

direct_query(E)    :- _set_assign(NAME,X,E).

representation(set,intensional).

%%%%%%%%%%%%%%%%% length
operator_declare(length,(set,()),int).
_computed(length,(ref(set,SET),()),val(int,N)) :- _compute(length,(ref(set,SET),())),
    N = #count { V : _set_contains(SET,V) }.

%%%%%%%%%%%%%%%%% set_declare set_assign set_value

_se_value(EX,ref(set,EX)) :- _set_declare(NAME,EX).

_compute(eq,(V1,(V2,()))) :-
    _set_assign(N1,EX,E1), _se_value(E1,V1),
    _set_assign(N2,EX,E2), _se_value(E2,V2), V1 < V2.
_set_contains(EX,V1) :-
    _set_assign(NAME,EX,E1), _se_value(E1,V1), %_se_value(EX,ref(set,ER)),
    #false : _set_assign(N2,EX,E2), _se_value(E2,V2), _computed(eq,(V2,(V1,())),val(bool,true)), V2 < V1.

_set_assign(NAME,EX,S) :- _set_assign(NAME,EX,ref(set,S)).

set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V).

%%%%%%%%%%%%%%%%% isin notin
operator_declare((isin;notin),(T1,(set,())),bool) :- _type(T1).
_compute(eq,(V1,(V2,())))  :- _compute((isin;notin),(V1,(ref(set,S),()))),
    _set_contains(S,V2).

_computed(isin,(V1,(ref(set,S),())),val(bool,true))   :- _compute(isin,(V1,(ref(set,S),()))),
    _set_contains(S,V2), _computed(eq,(V1,(V2,())),val(bool,true)).
_computed(isin,(V1,(ref(set,S),())),val(bool,false))  :- _compute(isin,(V1,(ref(set,S),()))),
    #false : _set_contains(S,V2), _computed(eq,(V1,(V2,())),val(bool,true)).
_computed(notin,(V1,(ref(set,S),())),val(bool,false)) :- _compute(notin,(V1,(ref(set,S),()))),
    _set_contains(S,V2), _computed(eq,(V1,(V2,())),val(bool,true)).
_computed(notin,(V1,(ref(set,S),())),val(bool,true))  :- _compute(notin,(V1,(ref(set,S),()))),
    #false : _set_contains(S,V2), _computed(eq,(V1,(V2,())),val(bool,true)).

%%%%%%%%%%%%%%%%% set_make
operator_declare_variadic(set_make,T,set,1) :- _type(T).
_set_declare(_internal,operation(set_make,L)) :- direct_query(operation(set_make,L)).
_set_assign(_internal,operation(set_make,L),SE) :- direct_query(operation(set_make,L)), SE=@pythonListElements(L).

_set_declare(_internal,set(L)) :- direct_query(set(L)).
_set_assign(_internal,set(L),SE) :- direct_query(set(L)), SE=@pythonListElements(L).

%%%%%%%%%%%%%%%%% filter
%%% TODO

%%%%%%%%%%%%%%%%%% add
%%% TODO

%%%%%%%%%%%%%%%%% union inter diff
operator_declare((union;inter;diff),(set,(set,())),set).
_set_declare(_internal,operation(OP,L)) :- direct_query(operation(OP,L)), OP = (diff;inter;union).
_set_assign(_internal,operation(union,L),V) :- direct_query(operation(union,L)), SE=@pythonListElements(L), _se_value(SE,ref(set,ER)), _set_contains(ER,V).

_compute(eq,(VSMALL,(VBIG,()))) :- direct_query(operation((diff;inter),(S1,(S2,())))),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,operation(inter,(S1,(S2,()))),VSMALL) :- direct_query(operation(inter,(S1,(S2,())))),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2), _computed(eq,(VSMALL,(VBIG,())),val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,operation(diff,(S1,(S2,()))),V1) :- direct_query(operation(diff,(S1,(S2,())))),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    #false : _set_contains(R2,V2), _computed(eq,(VSMALL,(VBIG,())),val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

%%%%%%%%%%%%%%%%% Equality
operator_declare((eq;neq),(set,(set,())),bool).
_compute(eq,(ARG1,(ARG2,()))) :- _compute(neq,(ARG1,(ARG2,()))), (ARG1;ARG2)=ref(set,X).
_computed(neq,(ARG1,(ARG2,())),val(bool,NEQ)) :- _computed(eq,(ARG1,(ARG2,())),val(bool,EQ)), (ARG1;ARG2)=ref(set,X), (EQ,NEQ)=((true,false);(false,true)).

_computed(eq,(ref(set,S1),(ref(set,S2),())),val(bool,true))  :- _compute(eq,(ref(set,S1),(ref(set,S2),()))), not _computed(eq,(ref(set,S1),(ref(set,S2),())),val(bool,false)).

_computed(eq,(ref(set,S1),(val(T2,S2),())),val(bool,false)) :- _compute(eq,(ref(set,S1),(val(T2,S2),()))), T2 != set.
_computed(eq,(val(T1,S1),(ref(set,S2),())),val(bool,false)) :- _compute(eq,(val(T1,S1),(ref(set,S2),()))), T1 != set.

_computed(eq,(ref(set,S1),(ref(set,S2),())),val(bool,false)) :- _compute(eq,(ref(set,S1),(ref(set,S2),()))),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _computed(eq,(V1,(V2,())),val(bool,true)).
_computed(eq,(ref(set,S1),(ref(set,S2),())),val(bool,false)) :- _compute(eq,(ref(set,S1),(ref(set,S2),()))),
    _set_contains(S2,V2),
    #false : _set_contains(S1,V1), _computed(eq,(V1,(V2,())),val(bool,true)).

_compute(eq,(V1,(V2,()))) :- _compute(eq,(ref(set,S1),(ref(set,S2),()))),
    _set_contains(S1,V1), _set_contains(S2,V2).

%%%%%%%%%%%%%%%%% Equality axioms

:- _computed(eq,(ref(set,X),(ref(set,X),())),val(bool,false)). %%% reflexivity
:- _computed(eq,(ref(set,X),(ref(set,Y),())),val(bool,true)),
   _computed(eq,(ref(set,Y),(ref(set,X),())),val(bool,false)). %%% symmetry
:- _computed(eq,(ref(set,L1),(ref(set,R1),())),val(bool,true)),
   _computed(eq,(ref(set,L2),(ref(set,R2),())),val(bool,true)),
   _computed(eq,(ref(set,L3),(ref(set,R3),())),val(bool,false)),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset
operator_declare(subset,(set,(set,())),bool).
_compute(eq,(V1,(V2,()))) :- _compute(subset,(ref(set,S1),(ref(set,S2),()))),
    _set_contains(S1,V1), _set_contains(S2,V2).
_computed(subset,(ref(set,S1),(ref(set,S2),())),val(bool,false)) :- _compute(subset,(ref(set,S1),(ref(set,S2),()))),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _computed(eq,(V1,(V2,())),val(bool,true)).

_computed(subset,(ref(set,S1),(ref(set,S2),())),val(bool,true))  :- _compute(subset,(ref(set,S1),(ref(set,S2),()))),
    not _computed(subset,(ref(set,S1),(ref(set,S2),())),val(bool,false)).
_computed(subset,(val(T1,S1),(val(T2,S2),())),val(bool,false)) :- _compute(subset,(val(T1,S1),(val(T2,S2),()))),
    (T1;T2) != set, (T1;T2) = set.

%%%%%%%%%%%%%%%%%% Fold
%%% set_fold: a -> b -> b

_set_makeIndex(VM) :- _compute(set_fold,(val(function,VO),(ref(set,VM),(ACC,())))).
_set_foldStep(set_fold,(val(function,VO),(ref(set,VM),(ACC,()))),0,ACC) :- _compute(set_fold,(val(function,VO),(ref(set,VM),(ACC,())))).
direct_query(operation(VO,(VI,(VB,())))) :- _compute(set_fold,(val(function,VO),(ref(set,VM),(ACC,())))),
    _set_index(VM,I,VI), _set_foldStep(set_fold,(val(function,VO),(ref(set,VM),(ACC,()))),I,VB).
_set_foldStep(set_fold,(val(function,VO),(ref(set,VM),(START,()))),I+1,NEXT) :- _compute(set_fold,(val(function,VO),(ref(set,VM),(START,())))),
    _set_foldStep(set_fold,(val(function,VO),(ref(set,VM),(START,()))),I,VB), _set_index(VM,I,VI),
    _se_value(operation(VO,(VI,(VB,()))),NEXT).
_computed(set_fold,(val(function,VO),(ref(set,VM),(START,()))),VB) :- _compute(set_fold,(val(function,VO),(ref(set,VM),(START,())))),
    _set_foldStep(set_fold,(val(function,VO),(ref(set,VM),(START,()))),I,VB),
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
_direct_imploded(ref(set,REF),V) :- _direct_implode(ref(set,REF)), _set_imploded(REF,V).
_direct_imploded(E,V) :- _direct_implode(E), _se_value(E,ref(set,REF)), _set_imploded(REF,V).

_direct_implode(val(TV,RV)) :- _set_implode(EM), _set_contains(EM,val(TV,RV)).
_set_makeIndex(EM) :- _set_implode(EM).
_set_as_list_aux(EM,0,()) :- _set_implode(EM).
_set_as_list_aux(EM,IDX+1,(V,L)) :- _set_as_list_aux(EM,IDX,L), _set_index(EM,IDX,val(TV,RV)), _direct_imploded(val(TV,RV),V).
_set_imploded(EM,set(L)) :- _set_as_list_aux(EM,IDX,L), _set_lastIndex(EM,IDX).

%_direct_imploded(E,E) :- _direct_implode(E), E = set(_).
