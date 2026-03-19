#defined set_declare/2.
#defined set_assign/3.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), set_assign(CNAME,X,EXPR).
_set_assign(CNAME,variable(X),E) :- engine(CNAME,compile), set_assign(CNAME,X,E).
_set_declare(CNAME,variable(X)) :- engine(CNAME,compile), set_declare(CNAME,X).

direct_query(E)    :- _set_assign(NAME,X,E).
_set_assign_id(NAME,EX,E_ID) :- _set_assign(NAME,EX,E), E_ID=@pythonId(E).

representation(set,intensional).

%%%%%%%%%%%%%%%%% length
operator_declare(OP,(T,()),int) :- T = set, OP = length.
_computedIdx_id(E_ID,val(int,N)) :- _computeIdx_id(E_ID, length),
    _computeIdx_id(E_ID, 0, ref(set,SET)),
    N = #count { V : _set_contains(SET,V) }.

%%%%%%%%%%%%%%%%% set_declare set_assign set_value

_se_value(EX,ref(set,EX)) :- _set_declare(NAME,EX).

_set_contains(EX,V1) :-
    _set_assign_id(NAME,EX,E1_ID), _se_value_id(E1_ID,V1),
    #false : _set_assign_id(N2,EX,E2_ID), _se_value_id(E2_ID,V2),
        _se_value(operation(eq,(V2,(V1,()))), val(bool,true)),
        V2 < V1.

% Request semantic equality checks between set-assigned values.
direct_query(operation(eq,(V1,(V2,())))) :-
    _set_assign_id(_,EX,E1_ID), _se_value_id(E1_ID,V1),
    _set_assign_id(_,EX,E2_ID), _se_value_id(E2_ID,V2).

_set_assign(NAME,EX,S) :- _set_assign(NAME,EX,ER), ER=ref(set,S).

set_value(X,V) :- _se_value(EX,ref(set,E)), _set_contains(E,V), EX=variable(X).

%%%%%%%%%%%%%%%%% isin notin
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1),T2=set, OP = (isin;notin).
direct_query(operation(eq,(V1,(V2,())))) :-
    _expr_id(E_ID,E),
    _computeIdx_id(E_ID, (isin;notin)),
    _computeIdx_id(E_ID, 0, V1),
    _computeIdx_id(E_ID, 1, ref(set,S)),
    _set_contains(S,V2).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, isin),
    _computeIdx_id(E_ID, 0, V1),
    _computeIdx_id(E_ID, 1, ref(set,S)),
    _set_contains(S,V2),
    _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, isin),
    _computeIdx_id(E_ID, 0, V1),
    _computeIdx_id(E_ID, 1, ref(set,S)),
    #false : _set_contains(S,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, notin),
    _computeIdx_id(E_ID, 0, V1),
    _computeIdx_id(E_ID, 1, ref(set,S)),
    _set_contains(S,V2),
    _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, notin),
    _computeIdx_id(E_ID, 0, V1),
    _computeIdx_id(E_ID, 1, ref(set,S)),
    #false : _set_contains(S,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

%%%%%%%%%%%%%%%%% set_make
operator_declare_variadic(set_make, T, set, 1) :- _type(T).
_set_declare(_internal,E) :- direct_query(E), E=operation(set_make,L).
_set_assign(_internal,E,SE) :- direct_query(E), E=operation(set_make,L), SE=@pythonListElements(L).

_set_declare(_internal,E) :- direct_query(E), E=set(L).
_set_assign(_internal,E,SE) :- direct_query(E), E=set(L), SE=@pythonListElements(L).

%%%%%%%%%%%%%%%%% filter
%%% TODO

%%%%%%%%%%%%%%%%%% add
%%% TODO

%%%%%%%%%%%%%%%%% union inter diff
operator_declare(OP,(T,(T,())),T) :- T = set, OP = (union;inter;diff).
_set_declare(_internal,E) :- direct_query(E), E=operation((diff;inter;union),L).
_set_assign(_internal,E,V) :- direct_query(E), E=operation(union,L), SE=@pythonListElements(L), SE_ID=@pythonId(SE), _se_value_id(SE_ID,ref(set,ER)), _set_contains(ER,V).

direct_query(operation(eq,(VSMALL,(VBIG,())))) :- direct_query(E), E=operation((diff;inter),L), L=(S1,(S2,())),
    S1_ID=@pythonId(S1), S2_ID=@pythonId(S2),
    _se_value_id(S1_ID,ref(set,R1)), _se_value_id(S2_ID,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,E,VSMALL) :- direct_query(E), E=operation(inter,L), L=(S1,(S2,())),
    S1_ID=@pythonId(S1), S2_ID=@pythonId(S2),
    _se_value_id(S1_ID,ref(set,R1)), _se_value_id(S2_ID,ref(set,R2)),
    _set_contains(R1,V1),
    _set_contains(R2,V2), _se_value(operation(eq,(VSMALL,(VBIG,()))), val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

_set_assign(_internal,E,V1) :- direct_query(E), E=operation(diff,L), L=(S1,(S2,())),
    S1_ID=@pythonId(S1), S2_ID=@pythonId(S2),
    _se_value_id(S1_ID,ref(set,R1)), _se_value_id(S2_ID,ref(set,R2)),
    _set_contains(R1,V1),
    #false : _set_contains(R2,V2), _se_value(operation(eq,(VSMALL,(VBIG,()))), val(bool,true)),
    (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL <= VBIG.

%%%%%%%%%%%%%%%%% Equality
operator_declare(OP,(T,(T,())),bool) :- T = set, OP = (eq;neq).
direct_query(operation(eq,(A,(B,())))) :- _expr_id(E_ID,E), _computeIdx_id(E_ID, neq), _computeIdx_id(E_ID, 0, A), _computeIdx_id(E_ID, 1, B).

_computedIdx_id(E_ID,val(bool,NEQ)) :- _computeIdx_id(E_ID, neq),
    _computeIdx_id(E_ID, 0, A),
    _computeIdx_id(E_ID, 1, B),
    _se_value(operation(eq,(A,(B,()))), val(bool,EQ)),
    (EQ,NEQ)=((true,false);(false,true)).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    not _computedIdx_id(E_ID,val(bool,false)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, ref(set,_)),
    _computeIdx_id(E_ID, 1, val(T2,_)),
    T2 != set.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(T1,_)),
    _computeIdx_id(E_ID, 1, ref(set,_)),
    T1 != set.

% Request element equality checks for set equality/subset.
direct_query(operation(eq,(V1,(V2,())))) :- _expr_id(E_ID,E), _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    _set_contains(S1,V1),
    _set_contains(S2,V2).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    _set_contains(S2,V2),
    #false : _set_contains(S1,V1), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

%%%%%%%%%%%%%%%%% Equality axioms

:- _expr_id(E_ID,E), _computedIdx_id(E_ID,val(bool,false)), E=operation(eq,(ref(set,X),(ref(set,X),()))). %%% reflexivity
:- _expr_id(E1_ID,E1), _computedIdx_id(E1_ID,val(bool,true)), E1=operation(eq,(ref(set,X),(ref(set,Y),()))),
   _expr_id(E2_ID,E2), _computedIdx_id(E2_ID,val(bool,false)), E2=operation(eq,(ref(set,Y),(ref(set,X),()))). %%% symmetry
:- _expr_id(E1_ID,E1), _computedIdx_id(E1_ID,val(bool,true)), E1=operation(eq,(ref(set,L1),(ref(set,R1),()))),
   _expr_id(E2_ID,E2), _computedIdx_id(E2_ID,val(bool,true)), E2=operation(eq,(ref(set,L2),(ref(set,R2),()))),
   _expr_id(E3_ID,E3), _computedIdx_id(E3_ID,val(bool,false)), E3=operation(eq,(ref(set,L3),(ref(set,R3),()))),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset
operator_declare(OP,(T,(T,())),bool) :- T = (set), OP = subset.
direct_query(operation(eq,(V1,(V2,())))) :- _expr_id(E_ID,E), _computeIdx_id(E_ID, subset),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    _set_contains(S1,V1),
    _set_contains(S2,V2).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, subset),
    _computeIdx_id(E_ID, 0, ref(set,S1)),
    _computeIdx_id(E_ID, 1, ref(set,S2)),
    _set_contains(S1,V1),
    #false : _set_contains(S2,V2), _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, subset),
    _computeIdx_id(E_ID, 0, ref(set,_)),
    _computeIdx_id(E_ID, 1, ref(set,_)),
    not _computedIdx_id(E_ID,val(bool,false)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, subset),
    _computeIdx_id(E_ID, 0, val(T1,_)),
    _computeIdx_id(E_ID, 1, val(T2,_)),
    (T1;T2) != set, (T1;T2) = set.

%%%%%%%%%%%%%%%%%% Fold
%%% set_fold: a -> b -> b
_set_makeIndex_id(E_ID,VM) :- _computeIdx_id(E_ID, set_fold), _computeIdx_id(E_ID, 1, ref(set,VM)).
_set_foldStep_id(E_ID,0,ACC) :- _computeIdx_id(E_ID, set_fold), _computeIdx_id(E_ID, 2, ACC).

direct_query(operation(VO,(VI,(VB,())))) :- _computeIdx_id(E_ID, set_fold),
    _computeIdx_id(E_ID, 0, val(function,VO)),
    _computeIdx_id(E_ID, 1, ref(set,VM)),
    _set_index(VM,I,VI),
    _set_foldStep_id(E_ID,I,VB).

_set_foldStep_id(E_ID,I+1,NEXT) :- _computeIdx_id(E_ID, set_fold),
    _computeIdx_id(E_ID, 0, val(function,VO)),
    _computeIdx_id(E_ID, 1, ref(set,VM)),
    _set_foldStep_id(E_ID,I,VB),
    _set_index(VM,I,VI),
    _se_value(operation(VO,(VI,(VB,()))), NEXT).

_computedIdx_id(E_ID,VB) :- _computeIdx_id(E_ID, set_fold),
    _computeIdx_id(E_ID, 1, ref(set,VM)),
    _set_foldStep_id(E_ID,I,VB),
    _set_lastIndex(VM,I).


_set_makeIndex(EM) :- _set_makeIndex_id(E_ID,EM).


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
