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
_computedIdx(E,val(int,N)) :- _computeIdx(E, length),
    _computeIdx(E, 0, ref(set,SET)),
    N = #count { V : _set_contains(SET,V) }.

%%%%%%%%%%%%%%%%% set_declare set_assign set_value

_se_value(EX,ref(set,EX)) :- _set_declare(NAME,EX).

_set_contains(EX,V1) :-
    _set_assign(NAME,EX,E1), _se_value(E1,V1), %_se_value(EX,ref(set,ER)),
    #false : _set_assign(N2,EX,E2), _se_value(E2,V2),
        _se_value(operation(eq,(V2,(V1,()))), val(bool,true)),
        V2 < V1.

% Request semantic equality checks between set-assigned values.
direct_query(operation(eq,(V1,(V2,())))) :-
    _set_assign(_,EX,E1), _se_value(E1,V1),
    _set_assign(_,EX,E2), _se_value(E2,V2).

_set_assign(NAME,EX,S) :- _set_assign(NAME,EX,ER), ER=ref(set,S).

set_value(X,V) :- _se_value(EX,ref(set,E)), _set_contains(E,V), EX=variable(X).

%%%%%%%%%%%%%%%%% isin notin
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1),T2=set, OP = (isin;notin).
direct_query(operation(eq,(V1,(V2,())))) :-
    _computeIdx(E, (isin;notin)),
    _computeIdx(E, 0, V1),
    _computeIdx(E, 1, ref(set,S)),
    _set_contains(S,V2).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, isin),
    _computeIdx(E, 0, V1),
    _computeIdx(E, 1, ref(set,S)),
    _set_contains(S,V2),
    _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, isin),
    _computeIdx(E, 0, V1),
    _computeIdx(E, 1, ref(set,S)),
    #false : _set_contains(S,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, notin),
    _computeIdx(E, 0, V1),
    _computeIdx(E, 1, ref(set,S)),
    _set_contains(S,V2),
    _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, notin),
    _computeIdx(E, 0, V1),
    _computeIdx(E, 1, ref(set,S)),
    #false : _set_contains(S,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

%%%%%%%%%%%%%%%%% set_make
operator_declare_variadic(set_make, T, set, 1) :- _type(T).
_set_declare(_internal,operation(set_make,L)) :- direct_query(operation(set_make,L)).
_set_assign(_internal,operation(set_make,L),SE) :- direct_query(operation(set_make,L)), SE=@pythonListElements(L).

_set_declare(_internal,set(L)) :- direct_query(set(L)).
_set_assign(_internal,set(L),SE) :- direct_query(set(L)), SE=@pythonListElements(L).

%%%%%%%%%%%%%%%%% filter
%%% TODO

%%%%%%%%%%%%%%%%%% add
%%% TODO

%%%%%%%%%%%%%%%%% union inter diff
operator_declare(OP,(T,(T,())),T) :- T = set, OP = (union;inter;diff).
_set_declare(_internal,operation(OP,L)) :- direct_query(operation(OP,L)), OP = (diff;inter;union).
_set_assign(_internal,operation(union,L),V) :- direct_query(operation(union,L)), SE=@pythonListElements(L), _se_value(SE,ref(set,ER)), _set_contains(ER,V).

direct_query(operation(eq,(VSMALL,(VBIG,())))) :- direct_query(operation((diff;inter),L)), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,operation(inter,L),VSMALL) :- direct_query(operation(inter,L)), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2), _se_value(operation(eq,(VSMALL,(VBIG,()))), val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,operation(diff,L),V1) :- direct_query(operation(diff,L)), L=(S1,(S2,())),
    _se_value(S1,ref(set,R1)), _se_value(S2,ref(set,R2)),
    _set_contains(R1,V1),
    #false : _set_contains(R2,V2), _se_value(operation(eq,(VSMALL,(VBIG,()))), val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

%%%%%%%%%%%%%%%%% Equality
operator_declare(OP,(T,(T,())),bool) :- T = set, OP = (eq;neq).
direct_query(operation(eq,(A,(B,())))) :- _computeIdx(E, neq), _computeIdx(E, 0, A), _computeIdx(E, 1, B).

_computedIdx(E,val(bool,NEQ)) :- _computeIdx(E, neq),
    _computeIdx(E, 0, A),
    _computeIdx(E, 1, B),
    _se_value(operation(eq,(A,(B,()))), val(bool,EQ)),
    (EQ,NEQ)=((true,false);(false,true)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    not _computedIdx(E,val(bool,false)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, ref(set,_)),
    _computeIdx(E, 1, val(T2,_)),
    T2 != set.

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, val(T1,_)),
    _computeIdx(E, 1, ref(set,_)),
    T1 != set.

% Request element equality checks for set equality/subset.
direct_query(operation(eq,(V1,(V2,())))) :- _computeIdx(E, eq),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    _set_contains(S1,V1),
    _set_contains(S2,V2).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, eq),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    _set_contains(S2,V2),
    #false : _set_contains(S1,V1), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

%%%%%%%%%%%%%%%%% Equality axioms

:- _computedIdx(E,val(bool,false)), E=operation(eq,(ref(set,X),(ref(set,X),()))). %%% reflexivity
:- _computedIdx(E1,val(bool,true)), E1=operation(eq,(ref(set,X),(ref(set,Y),()))),
   _computedIdx(E2,val(bool,false)), E2=operation(eq,(ref(set,Y),(ref(set,X),()))). %%% symmetry
:- _computedIdx(E1,val(bool,true)), E1=operation(eq,(ref(set,L1),(ref(set,R1),()))),
   _computedIdx(E2,val(bool,true)), E2=operation(eq,(ref(set,L2),(ref(set,R2),()))),
   _computedIdx(E3,val(bool,false)), E3=operation(eq,(ref(set,L3),(ref(set,R3),()))),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset
operator_declare(OP,(T,(T,())),bool) :- T = (set), OP = subset.
direct_query(operation(eq,(V1,(V2,())))) :- _computeIdx(E, subset),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    _set_contains(S1,V1),
    _set_contains(S2,V2).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, subset),
    _computeIdx(E, 0, ref(set,S1)),
    _computeIdx(E, 1, ref(set,S2)),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, subset),
    _computeIdx(E, 0, ref(set,_)),
    _computeIdx(E, 1, ref(set,_)),
    not _computedIdx(E,val(bool,false)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E, subset),
    _computeIdx(E, 0, val(T1,_)),
    _computeIdx(E, 1, val(T2,_)),
    (T1;T2) != set, (T1;T2) = set.

%%%%%%%%%%%%%%%%%% Fold
%%% set_fold: a -> b -> b
_set_makeIndex(VM) :- _computeIdx(E, set_fold), _computeIdx(E, 1, ref(set,VM)).
_set_foldStep(E,0,ACC) :- _computeIdx(E, set_fold), _computeIdx(E, 2, ACC).

direct_query(operation(VO,(VI,(VB,())))) :- _computeIdx(E, set_fold),
    _computeIdx(E, 0, val(function,VO)),
    _computeIdx(E, 1, ref(set,VM)),
    _set_index(VM,I,VI),
    _set_foldStep(E,I,VB).

_set_foldStep(E,I+1,NEXT) :- _computeIdx(E, set_fold),
    _computeIdx(E, 0, val(function,VO)),
    _computeIdx(E, 1, ref(set,VM)),
    _set_foldStep(E,I,VB),
    _set_index(VM,I,VI),
    _se_value(operation(VO,(VI,(VB,()))), NEXT).

_computedIdx(E,VB) :- _computeIdx(E, set_fold),
    _computeIdx(E, 1, ref(set,VM)),
    _set_foldStep(E,I,VB),
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
