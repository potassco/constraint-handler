#defined multimap_declare/2.
#defined multimap_assign/4.

engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_declare(CNAME,X).
engine(CNAME,ENG) :- _main_defaultEngine(ENG), not requestedEngine(CNAME), multimap_assign(CNAME,X,EKEY,EVAL).
_multimap_declare(CNAME,X) :- engine(CNAME,compile), multimap_declare(CNAME,X).
_multimap_assign(CNAME,X,EK,EV) :- engine(CNAME,compile), multimap_assign(CNAME,X,EK,EV).

direct_query(EK;EV) :- _multimap_assign(CNAME,X,EK,EV).

representation(multimap,intensional).

eValue(EX,multimap,X) :- _multimap_declare(CNAME,X), EX=variable(X), ER = ref(EX).
_multimap_add(ER,EK,EV) :- _multimap_assign(CNAME,X,EK,EV), EX = variable(X), eValue(EX,multimap,ER).

%%%%%%%%%%%%%%%%% pairstuples
direct_query(E1;E2) :- direct_query(E), E=(E1,E2).

%%%%%%%%%%%%%%%%% multimapMake

eValue(E,multimap,ER) :- direct_query(E), E=operation(multimapMake,L), ER=ref(E).
_multimap_add(ER,EK,EV) :- direct_query(E), E=operation(multimapMake,L), eValue(E,multimap,ER),
    (EK,EV)=@pythonListElements(L).

%%%%%%%%%%%%%%%%% multimap_assign multimap_value

_multimap_has(key,EM,TK,VK) :- _multimap_add(EM,EK,EV), eValue(EK,TK,VK).

compute(eq,(val(T,V1),(val(T,V2),()))) :- _multimap_has(D,E,T,V1), _multimap_has(D,E,T,V2),
    representation(T,intensional), V1 < V2.
_multimap_has(val(RK),EM,TV,VV) :- _multimap_add(EM,EK,EV),
    eValue(EK,TK,VK), eValue(EV,TV,VV),
    _multimap_representative(key,EM,TK,VK,RK).
_multimap_representative(D,E,T,V,R) :- _multimap_has(D,E,T,V),
    representation(T,intensional),
    _multimap_has(D,E,T,R), R <= V, #false : computed(eq,(val(T,R),(val(T,V),())),val(bool,false)), R != V;
    #count { W : _multimap_has(D,E,T,W), W < V, computed(eq,(val(T,W),(val(T,R),())),val(bool,true)) } = 0.

_multimap_representative(D,E,T,V,V) :- _multimap_has(D,E,T,V),
    representation(T,extensional).

_multimap_entry(EM,TK,RK,TV,RV) :- _multimap_add(EM,EK,EV),
    eValue(EK,TK,VK), _multimap_representative(key,EM,TK,VK,RK),
    eValue(EV,TV,VV), _multimap_representative(val(RK),EM,TV,VV,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,TK,VK,TV,VV) :- eValue(E,multimap,EM), _multimap_entry(EM,TK,VK,TV,VV), E=variable(X).

%%%%%%%%%%%%%%%%%% find

computed(O,ARGS,val(set,ref(find(ARGS)))) :- compute(O,ARGS), O=find, ARGS=(val(TK,RK),(val(multimap,EM),())).

_set_contains(ER,TV,RV) :- compute(O,ARGS), O=find, computed(O,ARGS,val(set,ER)),
    ARGS=(val(TK,RK),(val(multimap,EM),())),
    _multimap_entry(EM,TK,RK,TV,RV).

%%%%%%%%%%%%%%%%%% count keys and entries

computed(O,ARGS,val(int,N)) :- compute(O,ARGS), O=countKeys, ARGS=(val(multimap,EM),()),
    N = #count { TK,RK : _multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,val(int,N)) :- compute(O,ARGS), O=countEntries, ARGS=(val(multimap,EM),()),
    N = #count { TK,RK,TV,RV : _multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,val(int,N)) :- compute(O,ARGS), O=sumIntEntries, ARGS=(val(multimap,EM),()),
    N = #sum { RV,TK,RK : _multimap_entry(EM,TK,RK,int,RV) }.

computed(O,ARGS,val(T,M)) :- compute(O,ARGS), O=maxEntries, ARGS=(val(multimap,EM),()),
    (M,T) = #max { (RV,TV) : _multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,val(T,M)) :- compute(O,ARGS), O=minEntries, ARGS=(val(multimap,EM),()),
    (M,T) = #min { (RV,TV) : _multimap_entry(EM,TK,RK,TV,RV) }.

%%%%%%%%%%%%%%%%%% isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality
compute(eq,ARGS) :- compute(neq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())).
computed(neq,ARGS,val(bool,NEQ)) :- computed(eq,ARGS,val(bool,EQ)), ARGS = (val(T1,M1),(val(T2,M2),())), (T1;T2)=multimap, (EQ,NEQ)=((true,false);(false,true)).
computed(eq,ARGS,val(bool,true))  :- compute(eq,ARGS),  ARGS = (val(multimap,S1),(val(multimap,S2),())), not computed(eq,ARGS,val(bool,false)).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS),  ARGS = (val(T1,S1),(val(T2,S2),())), (T1;T2)=multimap, T1 != T2.

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,extensional),
    #false : _multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, RV1 = RV2.
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(vam(multimap,M2),())),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,extensional),
    #false : _multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, RV1 = RV2.

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,extensional),
    #false : _multimap_entry(M2,TK,RK2,TV,RV2), computed(eq,(val(TK,RK1),(val(TK,RK2),())),val(bool,true)), RV1 = RV2.
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,extensional),
    #false : _multimap_entry(M1,TK,RK1,TV,RV1), computed(eq,(val(TK,RK1),(val(TK,RK2),())),val(bool,true)), RV1 = RV2.

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,intensional),
    #false : _multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, computed(eq,(val(TV,RV1),(val(TV,RV2),())),val(bool,true)).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,intensional),
    #false : _multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, computed(eq,(val(TV,RV1),(val(TV,RV2),())),val(bool,true)).

computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,intensional),
    #false : _multimap_entry(M2,TK,RK2,TV,RV2), computed(eq,(val(TK,RK1),(val(TK,RK2),())),val(bool,true)), computed(eq,(val(TV,RV1),(val(TV,RV2),())),val(bool,true)).
computed(eq,ARGS,val(bool,false)) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,intensional),
    #false : _multimap_entry(M1,TK,RK1,TV,RV1), computed(eq,(val(TK,RK1),(val(TK,RK2),())),val(bool,true)), computed(eq,(val(TV,RV1),(val(TV,RV2),())),val(bool,true)).

compute(eq,SUBARGS) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional),
    SUBARGS=(val(TK,RK1),(val(TK,RK2),())).
compute(eq,SUBARGS) :- compute(eq,ARGS), ARGS = (val(multimap,M1),(val(multimap,M2),())),
    _multimap_entry(M1,TK,RK1,TV,RV1),
    _multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional),
    SUBARGS=(val(TV,RV1),(val(TV,RV2),())).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b

_multimap_makeIndex(VM) :- compute(multimap_fold,ARGS), ARGS = (val(function,VO),(val(multimap,VM),(val(TACC,VACC),()))).
_multimap_foldStep(multimap_fold,ARGS,0,TACC,VACC) :- compute(multimap_fold,ARGS), ARGS = (val(function,VO),(val(multimap,VM),(val(TACC,VACC),()))).
compute(VO,SUBARGS) :- compute(multimap_fold,ARGS), ARGS = (val(function,VO),(val(multimap,VM),(val(TSTART,VSTART),()))),
    _multimap_index(VM,I,TK,RK,TI,VI), _multimap_foldStep(multimap_fold,ARGS,I,TB,VB),
    SUBARGS = (val(TI,VI),(val(TB,VB),())).
_multimap_foldStep(multimap_fold,ARGS,I+1,TN,NEXT) :- compute(multimap_fold,ARGS), ARGS = (val(function,VO),(val(multimap,VM),(val(TSTART,VSTART),()))),
    _multimap_foldStep(multimap_fold,ARGS,I,TB,VB), _multimap_index(VM,I,TK,RK,TI,VI),
    SUBARGS = (val(TI,VI),(val(TB,VB),())),
    computed(VO,SUBARGS,val(TN,NEXT)).
computed(multimap_fold,ARGS,val(TB,VB)) :- compute(multimap_fold,ARGS), ARGS = (val(function,VO),(val(multimap,VM),(val(TSTART,VSTART),()))),
    _multimap_foldStep(multimap_fold,ARGS,I,TB,VB),
    _multimap_lastIndex(VM,I).

_multimap_index(EM,0,TK,RK,TV,RV) :- _multimap_makeIndex(EM),
    _multimap_entry(EM,TK,RK,TV,RV),
    #false : _multimap_entry(EM,TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_index(EM,I+1,TK,RK,TV,RV) :- _multimap_index(EM,I,TK0,RK0,TV0,RV0),
    _multimap_entry(EM,TK,RK,TV,RV), (TK0,RK0,TV0,RV0) < (TK,RK,TV,RV),
    #false : _multimap_entry(EM,TK1,RK1,TV1,RV1), (TK0,RK0,TV0,RV0) < (TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_lastIndex(EM,I+1) :- _multimap_index(EM,I,TK,RK,TV,RV),
    #false : _multimap_entry(EM,TK1,RK1,TV1,RV1), (TK,RK,TV,RV) < (TK1,RK1,TV1,RV1).

_multimap_lastIndex(EM,0) :- _multimap_makeIndex(EM),
    #false : _multimap_entry(EM,TK,RK,TV,RV).

%%%%%%%%%%%%%%%%%% isin

computed(O,ARGS,val(bool,true)) :- compute(O,ARGS), O=isin, ARGS=(val(TK,RK),(val(multimap,EM),())),
    _multimap_entry(EM,TK,RK,TV,RV).
computed(O,ARGS,val(bool,false)) :- compute(O,ARGS), O=isin, ARGS=(val(TK,RK),(val(multimap,EM),())),
    #false : _multimap_entry(EM,TK,RK,TV,RV).
