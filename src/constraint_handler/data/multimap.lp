#defined multimap_declare/2.
#defined multimap_assign/4.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_assign(CNAME,X,EKEY,EVAL).
_multimap_declare(CNAME,X) :- engine(CNAME,compile), multimap_declare(CNAME,X).
_multimap_assign(CNAME,variable(X),EK,EV) :- engine(CNAME,compile), multimap_assign(CNAME,X,EK,EV).
_multimap_assign_id(CNAME,EX,EK_ID,EV_ID) :- _multimap_assign(CNAME,EX,EK,EV), EK_ID=@pythonId(EK), EV_ID=@pythonId(EV).

direct_query(EK;EV) :- _multimap_assign(CNAME,EX,EK,EV).

representation(multimap,intensional).

_se_value(EX,val(multimap,EX)) :- _multimap_declare(CNAME,X), EX=variable(X), ER = ref(EX).
_multimap_add(ER,EK_ID,EV_ID) :- _multimap_assign_id(CNAME,EX,EK_ID,EV_ID), _se_value(EX,val(multimap,ER)).

%%%%%%%%%%%%%%%%% pairstuples
direct_query(E1;E2) :- direct_query(E), E=(E1,E2).

%%%%%%%%%%%%%%%%% multimap_make
operator_declare_variadic(multimap_make, (K,V), multimap, 1) :- _type(K), _type(V).
_se_value(E,val(multimap,ER)) :- direct_query(E), E=operation(multimap_make,L), ER=ref(E).
_multimap_add(ER,EK_ID,EV_ID) :- direct_query(E), E=operation(multimap_make,L), _se_value(E,val(multimap,ER)),
    (EK,EV)=@pythonListElements(L), EK_ID=@pythonId(EK), EV_ID=@pythonId(EV).

%%%%%%%%%%%%%%%%% multimap_assign multimap_value

_multimap_has(key,EM,K) :- _multimap_add(EM,EK_ID,EV_ID), _se_value_id(EK_ID,K).

% Request semantic equality checks between multimap keys/values when needed.
direct_query(operation(eq,(V1,(V2,())))) :- _multimap_has(D,E,V1), _multimap_has(D,E,V2).

_multimap_has(val(R),EM,V) :- _multimap_add(EM,EK_ID,EV_ID),
    _se_value_id(EK_ID,K), _se_value_id(EV_ID,V),
    _multimap_representative(key,EM,K,R).
_multimap_representative(D,E,V,R) :- _multimap_has(D,E,V),
    _multimap_has(D,E,R), R <= V, _se_value(operation(eq,(R,(V,()))), val(bool,true)),
    #false: _multimap_has(D,E,W), W < R, _se_value(operation(eq,(W,(R,()))), val(bool,true)).

_multimap_entry(EM,RK,RV) :- _multimap_add(EM,EK_ID,EV_ID),
    _se_value_id(EK_ID,K), _multimap_representative(key,EM,K,RK),
    _se_value_id(EV_ID,V), _multimap_representative(val(RK),EM,V,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,KEY,VAL) :- _se_value(E,val(multimap,EM)), _multimap_entry(EM,KEY,VAL), E=variable(X).

%%%%%%%%%%%%%%%%%% find
operator_declare(OP,(T1,(T2,())),set) :- _type(T1), T2 = multimap, OP = find.
%%% TODO: this is fragile, maybe buggy.
_computedIdx_id(E_ID,ref(set,find(ARGS))) :- _computeIdx_id(E_ID, find),
    _computeIdx_id(E_ID, 0, K),
    _computeIdx_id(E_ID, 1, val(multimap,EM)),
    ARGS=(K,(val(multimap,EM),())).

_set_contains(ER,V) :- _computedIdx_id(E_ID,ref(set,ER)), _computeIdx_id(E_ID, find),
    _computeIdx_id(E_ID, 0, K),
    _computeIdx_id(E_ID, 1, val(multimap,EM)),
    _multimap_entry(EM,K,V).

%%%%%%%%%%%%%%%%%% count keys and entries
operator_declare(OP,(T,()),int) :- T = multimap, OP = (countKeys;countEntries;sumIntEntries).
_computedIdx_id(E_ID,val(int,N)) :- _computeIdx_id(E_ID, countKeys), _computeIdx_id(E_ID, 0, val(multimap,EM)),
    N = #count { K : _multimap_entry(EM,K,V) }.

_computedIdx_id(E_ID,val(int,N)) :- _computeIdx_id(E_ID, countEntries), _computeIdx_id(E_ID, 0, val(multimap,EM)),
    N = #count { K,V : _multimap_entry(EM,K,V) }.

_computedIdx_id(E_ID,val(int,N)) :- _computeIdx_id(E_ID, sumIntEntries), _computeIdx_id(E_ID, 0, val(multimap,EM)),
    N = #sum { RV,K : _multimap_entry(EM,K,val(int,RV)) }.

%%%% TODO use type-specific greater/smaller than, instead of gringo's ordering.
_computedIdx_id(E_ID,M) :- _computeIdx_id(E_ID, maxEntries), _computeIdx_id(E_ID, 0, val(multimap,EM)),
    M = #max { V : _multimap_entry(EM,K,V) }.

_computedIdx_id(E_ID,M) :- _computeIdx_id(E_ID, minEntries), _computeIdx_id(E_ID, 0, val(multimap,EM)),
    M = #min { V : _multimap_entry(EM,K,V) }.

%%%%%%%%%%%%%%%%%% isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality
operator_declare(OP,(T,(T,())),bool) :- T = multimap, OP = (eq;neq).
direct_query(operation(eq,(A,(B,())))) :- _expr_id(E_ID,E), _computeIdx_id(E_ID, neq), _computeIdx_id(E_ID, 0, A), _computeIdx_id(E_ID, 1, B).

_computedIdx_id(E_ID,val(bool,NEQ)) :- _computeIdx_id(E_ID, neq),
    _computeIdx_id(E_ID, 0, A),
    _computeIdx_id(E_ID, 1, B),
    _se_value(operation(eq,(A,(B,()))), val(bool,EQ)),
    (EQ,NEQ)=((true,false);(false,true)).

% Request key/value equality checks for multimap equality.
direct_query(operation(eq,(X,(Y,())))) :- _expr_id(E_ID,E), _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(multimap,M1)),
    _computeIdx_id(E_ID, 1, val(multimap,M2)),
    _multimap_entry(M1,K1,V1),
    _multimap_entry(M2,K2,V2),
    (X,Y)=((K1,K2);(V1,V2)).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(multimap,_)),
    _computeIdx_id(E_ID, 1, val(multimap,_)),
    not _computedIdx_id(E_ID,val(bool,false)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(multimap,M1)),
    _computeIdx_id(E_ID, 1, val(multimap,M2)),
    _multimap_entry(M1,K1,V1),
    #false : _multimap_entry(M2,K2,V2),
        _se_value(operation(eq,(K1,(K2,()))), val(bool,true)),
        _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
    _computeIdx_id(E_ID, 0, val(multimap,M1)),
    _computeIdx_id(E_ID, 1, val(multimap,M2)),
    _multimap_entry(M2,K2,V2),
    #false : _multimap_entry(M1,K1,V1),
        _se_value(operation(eq,(K1,(K2,()))), val(bool,true)),
        _se_value(operation(eq,(V1,(V2,()))), val(bool,true)).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b
_multimap_makeIndex_id(E_ID,VM) :- _computeIdx_id(E_ID, multimap_fold), _computeIdx_id(E_ID, 1, val(multimap,VM)).
_multimap_foldStep_id(E_ID,0,ACC) :- _computeIdx_id(E_ID, multimap_fold), _computeIdx_id(E_ID, 2, ACC).

direct_query(operation(VO,(VI,(VB,())))) :- _computeIdx_id(E_ID, multimap_fold),
    _computeIdx_id(E_ID, 0, val(function,VO)),
    _computeIdx_id(E_ID, 1, val(multimap,VM)),
    _multimap_index(VM,I,_,VI),
    _multimap_foldStep_id(E_ID,I,VB).

_multimap_foldStep_id(E_ID,I+1,NEXT) :- _computeIdx_id(E_ID, multimap_fold),
    _computeIdx_id(E_ID, 0, val(function,VO)),
    _computeIdx_id(E_ID, 1, val(multimap,VM)),
    _multimap_foldStep_id(E_ID,I,VB),
    _multimap_index(VM,I,_,VI),
    _se_value(operation(VO,(VI,(VB,()))), NEXT).

_computedIdx_id(E_ID,VB) :- _computeIdx_id(E_ID, multimap_fold),
    _computeIdx_id(E_ID, 1, val(multimap,VM)),
    _multimap_foldStep_id(E_ID,I,VB),
    _multimap_lastIndex(VM,I).

_multimap_index(EM,0,K,V) :- _multimap_makeIndex_id(E_ID,EM),
    _multimap_entry(EM,K,V),
    #false : _multimap_entry(EM,K1,V1), (K1,V1) < (K,V).

_multimap_index(EM,I+1,K,V) :- _multimap_index(EM,I,K0,V0),
    _multimap_entry(EM,K,V), (K0,V0) < (K,V),
    #false : _multimap_entry(EM,K1,V1), (K0,V0) < (K1,V1), (K1,V1) < (K,V).

_multimap_lastIndex(EM,I+1) :- _multimap_index(EM,I,K,V),
    #false : _multimap_entry(EM,K1,V1), (K,V) < (K1,V1).

_multimap_lastIndex(EM,0) :- _multimap_makeIndex_id(E_ID,EM),
    #false : _multimap_entry(EM,K,V).

%%%%%%%%%%%%%%%%%% isin
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1),T2=multimap, OP = (isin).
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, isin),
    _computeIdx_id(E_ID, 0, K),
    _computeIdx_id(E_ID, 1, val(multimap,EM)),
    _multimap_entry(EM,K,_).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, isin),
    _computeIdx_id(E_ID, 0, K),
    _computeIdx_id(E_ID, 1, val(multimap,EM)),
    #false : _multimap_entry(EM,K,_).
