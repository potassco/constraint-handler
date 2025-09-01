#defined multimap_declare/2.
#defined multimap_assign/4.

representation(multimap,intensional).
_multimap_add(E,EK,EV) :- multimap_assign(CNAME,X,EK,EV), engine(CNAME,compile), E = variable(X).

direct_query(E) :- multimap_declare(NAME,X), E=variable(X).
direct_query(E;EK;EV) :- _multimap_add(E,EK,EV).

eValue(E,multimap,X) :- E=variable(X), multimap_declare(NAME,X).


%%%%%%%%%%%%%%%%% multimapMake

eValue(E,multimap,E) :- direct_query(E), E=operation(multimapMake,L).
_multimap_add(E,EK,EV) :- direct_query(E), E=operation(multimapMake,L),
    (EK,EV)=@pythonListElements(L,2).

%%%%%%%%%%%%%%%%% multimap_assign multimap_value

_multimap_has(key,EM,TK,VK) :- _multimap_add(E,EK,EV),
    eValue(E,multimap,EM), eValue(EK,TK,VK).

compute(eq,(T,(V1,(T,(V2,()))))) :- _multimap_has(D,E,T,V1), _multimap_has(D,E,T,V2),
    representation(T,intensional), V1 < V2.
_multimap_has(val(RK),EM,TV,VV) :- _multimap_add(E,EK,EV), eValue(E,multimap,EM),
    eValue(EK,TK,VK), eValue(EV,TV,VV),
    representative(key,EM,TK,VK,RK).
representative(D,E,T,V,R) :- _multimap_has(D,E,T,V),
    representation(T,intensional),
    _multimap_has(D,E,T,R), R <= V, #false : computed(eq,(T,(R,(T,(V,())))),bool,false), R != V;
    #count { W : _multimap_has(D,E,T,W), W < V, computed(eq,(T,(W,(T,(R,())))),bool,true) } = 0.

representative(D,E,T,V,V) :- _multimap_has(D,E,T,V),
    representation(T,extensional).

multimap_entry(EM,TK,RK,TV,RV) :- eValue(E,multimap,EM), _multimap_add(E,EK,EV),
    eValue(EK,TK,VK), representative(key,EM,TK,VK,RK),
    eValue(EV,TV,VV), representative(val(RK),EM,TV,VV,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,TK,VK,TV,VV) :- eValue(E,multimap,EM), multimap_entry(EM,TK,VK,TV,VV), E=variable(X).

%%%%%%%%%%%%%%%%%% find

computed(O,ARGS,TV,RV) :- compute(O,ARGS), O=find, ARGS=(TK,(RK,(multimap,(EM,())))),
    multimap_entry(EM,TK,RK,TV,RV).

%%%%%%%%%%%%%%%%%% count keys and entries

computed(O,ARGS,int,N) :- compute(O,ARGS), O=countKeys, ARGS=(multimap,(EM,())),
    N = #count { TK,RK : multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,int,N) :- compute(O,ARGS), O=countEntries, ARGS=(multimap,(EM,())),
    N = #count { TK,RK,TV,RV : multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,int,N) :- compute(O,ARGS), O=sumIntEntries, ARGS=(multimap,(EM,())),
    N = #sum { RV,TK,RK : multimap_entry(EM,TK,RK,int,RV) }.

computed(O,ARGS,T,M) :- compute(O,ARGS), O=maxEntries, ARGS=(multimap,(EM,())),
    (M,T) = #max { (RV,TV) : multimap_entry(EM,TK,RK,TV,RV) }.

computed(O,ARGS,T,M) :- compute(O,ARGS), O=minEntries, ARGS=(multimap,(EM,())),
    (M,T) = #min { (RV,TV) : multimap_entry(EM,TK,RK,TV,RV) }.

%%%%%%%%%%%%%%%%%% isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality
compute(eq,ARGS) :- compute(neq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))).
computed(neq,ARGS,bool,NEQ) :- computed(eq,ARGS,bool,EQ), ARGS = (T1,(M1,(T2,(M2,())))), (T1;T2)=multimap, (EQ,NEQ)=((true,false);(false,true)).
computed(eq,ARGS,bool,true)  :- compute(eq,ARGS),  ARGS = (multimap,(S1,(multimap,(S2,())))), not computed(eq,ARGS,bool,false).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS),  ARGS = (T1,(S1,(T2,(S2,())))), (T1;T2)=multimap, T1 != T2.

%computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
%    multimap_entry(M1,TK,RK,TV,RV), representation(TK,extensional), representation(TV,extensional),
%    not multimap_entry(M2,TK,RK,TV,RV).
%computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
%    multimap_entry(M2,TK,RK,TV,RV), representation(TK,extensional), representation(TV,extensional),
%    not multimap_entry(M1,TK,RK,TV,RV).

computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,extensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, RV1 = RV2.
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,extensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, RV1 = RV2.

computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,extensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), computed(eq,(TK,(RK1,(TK,(RK2,())))),bool,true), RV1 = RV2.
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,extensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), computed(eq,(TK,(RK1,(TK,(RK2,())))),bool,true), RV1 = RV2.

computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,intensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, computed(eq,(TV,(RV1,(TV,(RV2,())))),bool,true).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,intensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, computed(eq,(TV,(RV1,(TV,(RV2,())))),bool,true).

computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,intensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), computed(eq,(TK,(RK1,(TK,(RK2,())))),bool,true), computed(eq,(TV,(RV1,(TV,(RV2,())))),bool,true).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,intensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), computed(eq,(TK,(RK1,(TK,(RK2,())))),bool,true), computed(eq,(TV,(RV1,(TV,(RV2,())))),bool,true).

compute(eq,SUBARGS) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional),
    SUBARGS=(TK,(RK1,(TK,(RK2,())))).
compute(eq,SUBARGS) :- compute(eq,ARGS), ARGS = (multimap,(M1,(multimap,(M2,())))),
    multimap_entry(M1,TK,RK1,TV,RV1),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional),
    SUBARGS=(TV,(RV1,(TV,(RV2,())))).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b

_multimap_makeIndex(VM) :- compute(fold,ARGS), ARGS = (function,(VO,(multimap,(VM,(TACC,(VACC,())))))).
_multimap_foldStep(fold,ARGS,0,TACC,VACC) :- compute(fold,ARGS), ARGS = (function,(VO,(multimap,(VM,(TACC,(VACC,())))))).
compute(VO,SUBARGS) :- compute(fold,ARGS), ARGS = (function,(VO,(multimap,(VM,(TSTART,(VSTART,())))))),
    _multimap_index(VM,I,TK,RK,TI,VI), _multimap_foldStep(fold,ARGS,I,TB,VB),
    SUBARGS = (TI,(VI,(TB,(VB,())))).
_multimap_foldStep(fold,ARGS,I+1,TN,NEXT) :- compute(fold,ARGS), ARGS = (function,(VO,(multimap,(VM,(TSTART,(VSTART,())))))),
    _multimap_foldStep(fold,ARGS,I,TB,VB), _multimap_index(VM,I,TK,RK,TI,VI),
    SUBARGS = (TI,(VI,(TB,(VB,())))),
    computed(VO,SUBARGS,TN,NEXT).
computed(fold,ARGS,TB,VB) :- compute(fold,ARGS), ARGS = (function,(VO,(multimap,(VM,(TSTART,(VSTART,())))))),
    _multimap_foldStep(fold,ARGS,I,TB,VB),
    _multimap_lastIndex(VM,I).

_multimap_index(EM,0,TK,RK,TV,RV) :- _multimap_makeIndex(EM),
    multimap_entry(EM,TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_index(EM,I+1,TK,RK,TV,RV) :- _multimap_index(EM,I,TK0,RK0,TV0,RV0),
    multimap_entry(EM,TK,RK,TV,RV), (TK0,RK0,TV0,RV0) < (TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK0,RK0,TV0,RV0) < (TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_lastIndex(EM,I+1) :- _multimap_index(EM,I,TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK,RK,TV,RV) < (TK1,RK1,TV1,RV1).

_multimap_lastIndex(EM,0) :- _multimap_makeIndex(EM),
    #false : multimap_entry(EM,TK,RK,TV,RV).
