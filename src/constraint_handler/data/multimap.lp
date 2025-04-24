#defined multimap_declare/2.
#defined multimap_assign/4.

representation(multimap,intensional).
_multimap_add(E,EK,EV) :- multimap_assign(CNAME,X,EK,EV), engine(CNAME,compile), E = variable(X).

expression(E) :- multimap_declare(NAME,X), E=variable(X).
expression(E;EK;EV) :- _multimap_add(E,EK,EV).

eValue(E,multimap,symbol(E)) :- E=variable(X), multimap_declare(NAME,X).
eValue(E,multimap,E) :- expression(E), E=operation(multimapMake,L).
_multimap_add(E,EK,EV) :- expression(E), E=operation(multimapMake,L),
    (EK,EV)=@pythonListElements(L,2).

%%%%%%%%%%%%%%%%% multimap_assign multimap_value

multimapHas(key,EM,TK,VK) :- _multimap_add(E,EK,EV),
    eValue(E,multimap,EM), eValue(EK,TK,VK).

testEqual(T,V1,V2) :- multimapHas(D,E,T,V1), multimapHas(D,E,T,V2),
    representation(T,intensional), V1 < V2.
multimapHas(val(RK),EM,TV,VV) :- _multimap_add(E,EK,EV), eValue(E,multimap,EM),
    eValue(EK,TK,VK), eValue(EV,TV,VV),
    representative(key,EM,TK,VK,RK).
representative(D,E,T,V,R) :- multimapHas(D,E,T,V),
    representation(T,intensional),
    multimapHas(D,E,T,R), R <= V, #false : not testedEqual(T,R,V), R != V;
    #count { W : multimapHas(D,E,T,W), W < V, testedEqual(T,W,R) } = 0.

representative(D,E,T,V,V) :- multimapHas(D,E,T,V),
    representation(T,extensional).

multimap_entry(EM,TK,RK,TV,RV) :- eValue(E,multimap,EM), _multimap_add(E,EK,EV),
    eValue(EK,TK,VK), representative(key,EM,TK,VK,RK),
    eValue(EV,TV,VV), representative(val(RK),EM,TV,VV,RV).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

multimap_value(X,TK,VK,TV,VV) :- eValue(E,multimap,EM), multimap_entry(EM,TK,VK,TV,VV), E=variable(X).

%%%%%%%%%%%%%%%%%% count keys and entries

eValue(E,int,N) :- expression(E), E=operation(countKeys,(MAP,())), eValue(MAP,multimap,EM),
    N = #count { TK,RK : multimap_entry(EM,TK,RK,TV,RV) }.

eValue(E,int,N) :- expression(E), E=operation(countEntries,(MAP,())), eValue(MAP,multimap,EM),
    N = #count { TK,RK,TV,RV : multimap_entry(EM,TK,RK,TV,RV) }.

eValue(E,int,N) :- expression(E), E=operation(sumIntEntries,(MAP,())), eValue(MAP,multimap,EM),
    N = #sum { RV,TK,RK : multimap_entry(EM,TK,RK,int,RV) }.

eValue(E,T,M) :- expression(E), E=operation(maxEntries,(MAP,())), eValue(MAP,multimap,EM),
    (M,T) = #max { (RV,TV) : multimap_entry(EM,TK,RK,TV,RV) }.
eValue(E,T,M) :- expression(E), E=operation(minEntries,(MAP,())), eValue(MAP,multimap,EM),
    (M,T) = #max { (RV,TV) : multimap_entry(EM,TK,RK,TV,RV) }.

%%%%%%%%%%%%%%%%%% isin notin

%%%%%%%%%%%%%%%%%% union inter

%%%%%%%%%%%%%%%%%% Equality

testEqual(multimap,S1,S2) :- expression(E), E=operation((eq;neq),L), L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,multimap,S2).
eValue(E,bool,true)  :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,multimap,S2), testedEqual(multimap,S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,multimap,S2), testedDifferent(multimap,S1,S2).
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,multimap,S2), testedDifferent(multimap,S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,multimap,S2), testedEqual(multimap,S1,S2).

eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,T2,S2), T2 != multimap.
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,multimap,S1), eValue(E2,T2,S2), T2 != multimap.
eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,multimap,S2), T1 != multimap.
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,multimap,S2), T1 != multimap.

%testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
%    multimap_entry(M1,TK,RK,TV,RV), representation(TK,extensional), representation(TV,extensional),
%    not multimap_entry(M2,TK,RK,TV,RV).
%testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
%    multimap_entry(M2,TK,RK,TV,RV), representation(TK,extensional), representation(TV,extensional),
%    not multimap_entry(M1,TK,RK,TV,RV).

testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,extensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, RV1 = RV2.
testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,extensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, RV1 = RV2.

testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,extensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), testedEqual(TK,RK1,RK2), RV1 = RV2.
testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,extensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), testedEqual(TK,RK1,RK2), RV1 = RV2.

testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,extensional), representation(TV,intensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), RK1 = RK2, testedEqual(TV,RV1,RV2).
testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,extensional), representation(TV,intensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), RK1 = RK2, testedEqual(TV,RV1,RV2).

testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1), representation(TK,intensional), representation(TV,intensional),
    #false : multimap_entry(M2,TK,RK2,TV,RV2), testedEqual(TK,RK1,RK2), testedEqual(TV,RV1,RV2).
testedDifferent(multimap,M1,M2) :- testEqual(multimap,M1,M2),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional), representation(TV,intensional),
    #false : multimap_entry(M1,TK,RK1,TV,RV1), testedEqual(TV,RK1,RK2), testedEqual(TV,RV1,RV2).

testEqual(TK,RK1,RK2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TK,intensional).
testEqual(TV,RV1,RV2) :- testEqual(multimap,M1,M2),
    multimap_entry(M1,TK,RK1,TV,RV1),
    multimap_entry(M2,TK,RK2,TV,RV2), representation(TV,intensional).
testedEqual(multimap,V1,V2) :- testEqual(multimap,V1,V2), not testedDifferent(multimap,V1,V2).

%%%%%%%%%%%%%%%%%% Fold
%%% fold: a -> b -> b

_multimap_makeIndex(EM) :- expression(E), E=operation(fold,(EOP,(MAP,(START,())))), eValue(MAP,multimap,EM).
_multimap_foldStep(E,0,TB,VB) :- expression(E), E=operation(fold,(EOP,(MAP,(START,())))),
    eValue(MAP,multimap,EM), eValue(START,TB,VB).
compute(OP,ARGS) :- expression(E), E=operation(fold,(EOP,(MAP,(START,())))),
    eValue(MAP,multimap,EM), eValue(EOP,symbol,OP),
    _multimap_index(EM,I,TK,RK,TA,VA), _multimap_foldStep(E,I,TB,VB),
    ARGS = (TA,(VA,(TB,(VB,())))).
_multimap_foldStep(E,I+1,TN,NEXT) :- expression(E), E=operation(fold,(EOP,(MAP,(START,())))),
    eValue(MAP,multimap,EM), eValue(EOP,symbol,OP),
    _multimap_foldStep(E,I,TB,VB), _multimap_index(EM,I,TK,RK,TA,VA),
    ARGS = (TA,(VA,(TB,(VB,())))),
    computed(OP,ARGS,TN,NEXT).
eValue(E,TB,VB) :- expression(E), E=operation(fold,(EOP,(MAP,(START,())))),
    eValue(MAP,multimap,EM),
    _multimap_foldStep(E,I,TB,VB),
    _multimap_lastIndex(EM,I).

_multimap_index(EM,0,TK,RK,TV,RV) :- _multimap_makeIndex(EM),
    multimap_entry(EM,TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_index(EM,I+1,TK,RK,TV,RV) :- _multimap_index(EM,I,TK0,RK0,TV0,RV0),
    multimap_entry(EM,TK,RK,TV,RV), (TK0,RK0,TV0,RV0) < (TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK0,RK0,TV0,RV0) < (TK1,RK1,TV1,RV1), (TK1,RK1,TV1,RV1) < (TK,RK,TV,RV).

_multimap_lastIndex(EM,I+1) :- _multimap_index(EM,I,TK,RK,TV,RV),
    #false : multimap_entry(EM,TK1,RK1,TV1,RV1), (TK,RK,TV,RV) < (TK1,RK1,TV1,RV1).
