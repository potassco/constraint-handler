#defined multimap_declare/1.
#defined multimap_assign/3.

multimap_declare(_label_anonymous,X) :- multimap_declare(X).
multimap_assign(_label_anonymous,X,EKEY,EVAL) :- multimap_assign(X,EKEY,EVAL).

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_assign(CNAME,X,EKEY,EVAL).
_multimap_declare(CNAME,X) :- engine(CNAME,compile), multimap_declare(CNAME,X).
_multimap_assign(CNAME,variable(X),EK,EV) :- engine(CNAME,compile), multimap_assign(CNAME,X,EK,EV).

direct_query(EK;EV) :- _multimap_assign(CNAME,EX,EK,EV).

representation(multimap,intensional).

_se_value(variable(X),val(multimap,variable(X))) :- _multimap_declare(CNAME,X), ER = ref(variable(X)).
_multimap_add(ER,EK,EV) :- _multimap_assign(CNAME,EX,EK,EV), _se_value(EX,val(multimap,ER)).

%%%%%%%%%%%%%%%%% pairstuples
direct_query(E1;E2) :- direct_query((E1,E2)).

%%%%%%%%%%%%%%%%% multimap_make
operator_declare_variadic(multimap_make,(K,V),multimap,1) :- _type(K), _type(V).
_se_value(operation(multimap_make,L),val(multimap,ref(operation(multimap_make,L)))) :- direct_query(operation(multimap_make,L)).
_multimap_add(ER,EK,EV) :- direct_query(operation(multimap_make,L)), _se_value(operation(multimap_make,L),val(multimap,ER)),
    (EK,EV)=@pythonListElements(L).

%%%%%%%%%%%%%%%%% multimap_assign multimap_value

_multimap_has(key,EM,K) :- _multimap_add(EM,EK,EV), _se_value(EK,K).

direct_query(operation(eq,(V1,(V2,())))) :- _multimap_has(D,E,V1), _multimap_has(D,E,V2), V1 <= V2.

_multimap_has(val(R),EM,V) :- _multimap_add(EM,EK,EV),
    _se_value(EK,K), _se_value(EV,V),
    _multimap_representative(key,EM,K,R).
_multimap_representative(D,E,V,R) :- _multimap_has(D,E,V),
    _multimap_has(D,E,R), R <= V, _se_value(operation(eq,(R,(V,()))),val(bool,true)),
    #false: _multimap_has(D,E,W), W < R, _se_value(operation(eq,(W,(R,()))),val(bool,true)).

_multimap_entry(EM,RK,RV) :- _multimap_add(EM,EK,EV),
    _se_value(EK,K), _multimap_representative(key,EM,K,RK),
    _se_value(EV,V), _multimap_representative(val(RK),EM,V,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,KEY,VAL) :- _se_value(variable(X),val(multimap,EM)), _multimap_entry(EM,KEY,VAL).

%%%%%%%%%%%%%%%%%% find
operator_declare(find,(T1,(multimap,())),set) :- _type(T1).
%%% TODO: this is fragile, maybe buggy.
_computedIdx(E,ref(set,find((K,(val(multimap,EM),()))))) :- _computeIdx(E,find), _computeIdx(E,0,K), _computeIdx(E,1,val(multimap,EM)).

_set_contains(ER,V) :- _computedIdx(E,ref(set,ER)), _computeIdx(E,find), _computeIdx(E,0,K), _computeIdx(E,1,val(multimap,EM)),
    _multimap_entry(EM,K,V).

%%%%%%%%%%%%%%%%%% count keys and entries
operator_declare((countKeys;countEntries;sumIntEntries),(multimap,()),int).
_computedIdx(E,val(int,N)) :- _computeIdx(E,countKeys), _computeIdx(E,0,val(multimap,EM)),
    N = #count { K : _multimap_entry(EM,K,V) }.

_computedIdx(E,val(int,N)) :- _computeIdx(E,countEntries), _computeIdx(E,0,val(multimap,EM)),
    N = #count { K,V : _multimap_entry(EM,K,V) }.

_computedIdx(E,val(int,N)) :- _computeIdx(E,sumIntEntries), _computeIdx(E,0,val(multimap,EM)),
    N = #sum { RV,K : _multimap_entry(EM,K,val(int,RV)) }.

%%%% TODO use type-specific greater/smaller than, instead of gringo's ordering.
_computedIdx(E,M) :- _computeIdx(E,maxEntries), _computeIdx(E,0,val(multimap,EM)),
    M = #max { V : _multimap_entry(EM,K,V) }.

_computedIdx(E,M) :- _computeIdx(E,minEntries), _computeIdx(E,0,val(multimap,EM)),
    M = #min { V : _multimap_entry(EM,K,V) }.

%%%%%%%%%%%%%%%%%% multimap_isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality
operator_declare((eq;neq),(multimap,(multimap,())),bool).

direct_query(operation(eq,(val(multimap,M0),(val(multimap,M1),())))) :- _computeIdx(E,neq), _computeIdx(E,0,val(multimap,M0)), _computeIdx(E,1,val(multimap,M1)).

_computedIdx(E,val(bool,NEQ)) :- _computeIdx(E,neq), _computeIdx(E,0,val(T0,M0)), _computeIdx(E,1,val(T1,M1)), (T0;T1)=multimap,
    _se_value(operation(eq,(val(T0,M0),(val(T1,M1),()))),val(bool,EQ)),
    (EQ,NEQ)=((true,false);(false,true)).

direct_query(operation(eq,(X,(Y,())))) :- _computeIdx(E,eq), _computeIdx(E,0,val(multimap,M1)), _computeIdx(E,1,val(multimap,M2)),
    _multimap_entry(M1,K1,V1),
    _multimap_entry(M2,K2,V2),
    (X,Y)=((K1,K2);(V1,V2)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,eq), _computeIdx(E,0,val(multimap,_)), _computeIdx(E,1,val(multimap,_)),
    not _computedIdx(E,val(bool,false)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(multimap,M1)), _computeIdx(E,1,val(multimap,M2)),
    _multimap_entry(M1,K1,V1),
    #false : _multimap_entry(M2,K2,V2), _se_value(operation(eq,(K1,(K2,()))),val(bool,true)), _se_value(operation(eq,(V1,(V2,()))),val(bool,true)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq), _computeIdx(E,0,val(multimap,M1)), _computeIdx(E,1,val(multimap,M2)),
    _multimap_entry(M2,K2,V2),
    #false : _multimap_entry(M1,K1,V1), _se_value(operation(eq,(K1,(K2,()))),val(bool,true)), _se_value(operation(eq,(V1,(V2,()))),val(bool,true)).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b
_multimap_makeIndex(VM) :- _computeIdx(E,multimap_fold), _computeIdx(E,1,val(multimap,VM)).
_multimap_foldStep(E,0,ACC) :- _computeIdx(E,multimap_fold), _computeIdx(E,2,ACC).

direct_query(operation(VO,(VI,(VB,())))) :- _computeIdx(E,multimap_fold), _computeIdx(E,0,val(function,VO)), _computeIdx(E,1,val(multimap,VM)),
    _multimap_index(VM,I,_,VI), _multimap_foldStep(E,I,VB).
_multimap_foldStep(E,I+1,NEXT) :- _computeIdx(E,multimap_fold), _computeIdx(E,0,val(function,VO)), _computeIdx(E,1,val(multimap,VM)),
    _multimap_foldStep(E,I,VB), _multimap_index(VM,I,_,VI),
    _se_value(operation(VO,(VI,(VB,()))),NEXT).

_computedIdx(E,VB) :- _computeIdx(E, multimap_fold), _computeIdx(E,1,val(multimap,VM)),
    _multimap_foldStep(E,I,VB), _multimap_lastIndex(VM,I).


_multimap_index(EM,0,K,V) :- _multimap_makeIndex(EM),
    _multimap_entry(EM,K,V),
    #false : _multimap_entry(EM,K1,V1), (K1,V1) < (K,V).

_multimap_index(EM,I+1,K,V) :- _multimap_index(EM,I,K0,V0),
    _multimap_entry(EM,K,V), (K0,V0) < (K,V),
    #false : _multimap_entry(EM,K1,V1), (K0,V0) < (K1,V1), (K1,V1) < (K,V).

_multimap_lastIndex(EM,I+1) :- _multimap_index(EM,I,K,V),
    #false : _multimap_entry(EM,K1,V1), (K,V) < (K1,V1).

_multimap_lastIndex(EM,0) :- _multimap_makeIndex(EM),
    #false : _multimap_entry(EM,K,V).

%%%%%%%%%%%%%%%%%% multimap_isin
operator_declare(multimap_isin,(T1,(multimap,())),bool) :- _type(T1).
_computedIdx(E,val(bool,true)) :- _computeIdx(E,multimap_isin), _computeIdx(E,0,K), _computeIdx(E,1,val(multimap,EM)),
    _multimap_entry(EM,K,_).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,multimap_isin), _computeIdx(E,0,K), _computeIdx(E,1,val(multimap,EM)),
    #false : _multimap_entry(EM,K,_).
