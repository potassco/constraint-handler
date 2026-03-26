#defined multimap_declare/2.
#defined multimap_assign/4.

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

_compute(eq,(V1,(V2,()))) :- _multimap_has(D,E,V1), _multimap_has(D,E,V2), V1 <= V2.
_multimap_has(val(R),EM,V) :- _multimap_add(EM,EK,EV),
    _se_value(EK,K), _se_value(EV,V),
    _multimap_representative(key,EM,K,R).
_multimap_representative(D,E,V,R) :- _multimap_has(D,E,V),
    _multimap_has(D,E,R), R <= V, _computed(eq,(R,(V,())),val(bool,true)),
    #false: _multimap_has(D,E,W), W < R, _computed(eq,(W,(R,())),val(bool,true)).

_multimap_entry(EM,RK,RV) :- _multimap_add(EM,EK,EV),
    _se_value(EK,K), _multimap_representative(key,EM,K,RK),
    _se_value(EV,V), _multimap_representative(val(RK),EM,V,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,KEY,VAL) :- _se_value(variable(X),val(multimap,EM)), _multimap_entry(EM,KEY,VAL).

%%%%%%%%%%%%%%%%%% find
operator_declare(find,(T1,(multimap,())),set) :- _type(T1).
%%% TODO: this is fragile, maybe buggy.
_computed(find,(K,(val(multimap,EM),())),ref(set,find((K,(val(multimap,EM),()))))) :- _compute(find,(K,(val(multimap,EM),()))).

_set_contains(ER,V) :- _compute(find,(K,(val(multimap,EM),()))), _computed(find,(K,(val(multimap,EM),())),ref(set,ER)),
    _multimap_entry(EM,K,V).

%%%%%%%%%%%%%%%%%% count keys and entries
operator_declare((countKeys;countEntries;sumIntEntries),(multimap,()),int).
_computed(countKeys,(val(multimap,EM),()),val(int,N)) :- _compute(countKeys,(val(multimap,EM),())),
    N = #count { K : _multimap_entry(EM,K,V) }.

_computed(countEntries,(val(multimap,EM),()),val(int,N)) :- _compute(countEntries,(val(multimap,EM),())),
    N = #count { K,V : _multimap_entry(EM,K,V) }.

_computed(sumIntEntries,(val(multimap,EM),()),val(int,N)) :- _compute(sumIntEntries,(val(multimap,EM),())),
    N = #sum { RV,K : _multimap_entry(EM,K,val(int,RV)) }.

%%%% TODO use type-specific greater/smaller than, instead of gringo's ordering.
_computed(maxEntries,(val(multimap,EM),()),M) :- _compute(maxEntries,(val(multimap,EM),())),
    M = #max { V : _multimap_entry(EM,K,V) }.

_computed(minEntries,(val(multimap,EM),()),M) :- _compute(minEntries,(val(multimap,EM),())),
    M = #min { V : _multimap_entry(EM,K,V) }.

%%%%%%%%%%%%%%%%%% isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality
operator_declare((eq;neq),(multimap,(multimap,())),bool).
_compute(eq,(val(multimap,M1),(val(multimap,M2),()))) :- _compute(neq,(val(multimap,M1),(val(multimap,M2),()))).
_computed(neq,(val(T1,M1),(val(T2,M2),())),val(bool,NEQ)) :- _computed(eq,(val(T1,M1),(val(T2,M2),())),val(bool,EQ)), (T1;T2)=multimap, (EQ,NEQ)=((true,false);(false,true)).
_computed(eq,(val(multimap,S1),(val(multimap,S2),())),val(bool,true)) :- _compute(eq,(val(multimap,S1),(val(multimap,S2),()))), not _computed(eq,(val(multimap,S1),(val(multimap,S2),())),val(bool,false)).

_computed(eq,(val(multimap,M1),(val(multimap,M2),())),val(bool,false)) :- _compute(eq,(val(multimap,M1),(val(multimap,M2),()))),
    _multimap_entry(M1,K1,V1),
    #false : _multimap_entry(M2,K2,V2), _computed(eq,(K1,(K2,())),val(bool,true)), _computed(eq,(V1,(V2,())),val(bool,true)).
_computed(eq,(val(multimap,M1),(val(multimap,M2),())),val(bool,false)) :- _compute(eq,(val(multimap,M1),(val(multimap,M2),()))),
    _multimap_entry(M2,K2,V2),
    #false : _multimap_entry(M1,K1,V1), _computed(eq,(K1,(K2,())),val(bool,true)), _computed(eq,(V1,(V2,())),val(bool,true)).


_compute(eq,(K1,(K2,()))) :- _compute(eq,(val(multimap,M1),(val(multimap,M2),()))),
    _multimap_entry(M1,K1,V1),
    _multimap_entry(M2,K2,V2).
_compute(eq,(V1,(V2,()))) :- _compute(eq,(val(multimap,M1),(val(multimap,M2),()))),
    _multimap_entry(M1,K1,V1),
    _multimap_entry(M2,K2,V2).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b

_multimap_makeIndex(VM) :- _compute(multimap_fold,(val(function,VO),(val(multimap,VM),(ACC,())))).
_multimap_foldStep(multimap_fold,(val(function,VO),(val(multimap,VM),(ACC,()))),0,ACC) :- _compute(multimap_fold,(val(function,VO),(val(multimap,VM),(ACC,())))).
direct_query(operation(VO,(VI,(VB,())))) :- _compute(multimap_fold,(val(function,VO),(val(multimap,VM),(START,())))),
    _multimap_index(VM,I,K,VI), _multimap_foldStep(multimap_fold,(val(function,VO),(val(multimap,VM),(START,()))),I,VB).
_multimap_foldStep(multimap_fold,(val(function,VO),(val(multimap,VM),(START,()))),I+1,NEXT) :- _compute(multimap_fold,(val(function,VO),(val(multimap,VM),(START,())))),
    _multimap_foldStep(multimap_fold,(val(function,VO),(val(multimap,VM),(START,()))),I,VB), _multimap_index(VM,I,K,VI),
    _se_value(operation(VO,(VI,(VB,()))),NEXT).
_computed(multimap_fold,(val(function,VO),(val(multimap,VM),(START,()))),VB) :- _compute(multimap_fold,(val(function,VO),(val(multimap,VM),(START,())))),
    _multimap_foldStep(multimap_fold,(val(function,VO),(val(multimap,VM),(START,()))),I,VB),
    _multimap_lastIndex(VM,I).

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

%%%%%%%%%%%%%%%%%% isin
operator_declare(isin,(T1,(multimap,())),bool) :- _type(T1).
_computed(isin,(K,(val(multimap,EM),())),val(bool,true)) :- _compute(isin,(K,(val(multimap,EM),()))),
    _multimap_entry(EM,K,V).
_computed(isin,(K,(val(multimap,EM),())),val(bool,false)) :- _compute(isin,(K,(val(multimap,EM),()))),
    #false : _multimap_entry(EM,K,V).
