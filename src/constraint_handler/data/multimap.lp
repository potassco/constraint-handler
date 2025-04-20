representation(multimap,intensional).
_multimap_add(E,EK,EV) :- multimap_assign(CNAME,X,EK,EV), engine(CNAME,compile), E = variable(X).
%compileAssignToMultimap(CNAME,X,EK,EV) :- multimap_assign(CNAME,X,EK,EV), engine(CNAME,compile).
%_multimap_add(E,EK,EV) :- compileAssignToMultimap(NAME,X,EK,EV), E = variable(X).

expression(E) :- multimap_declare(NAME,X), E=variable(X).
expression(E;EK;EV) :- _multimap_add(E,EK,EV).
%expression(E;EK;EV) :- compileAssignToMultimap(NAME,X,EK,EV), E=variable(X).
%expression(EK;EV) :- expression(E), E=operation(multimapMake,L),
%    (EK,EV)=@pythonListElements(L).

%eValue(E,multimap,symbol(E)) :- E=variable(X), compileAssignToMultimap(NAME,X,EK,EV).
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
%testEqual(T,V1,V2) :- multimapHas(D,E,T,V1), multimapHas(D,E,T,V2),
%    representation(T,intensional), V1 < V2.
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

%% count keys and entries

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
%%%%%%%%%%%%%%%%% isin notin

%
%%%%%%%%%%%%%%%%%% union inter
%
%testEqual(T,V1,V2) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V1 < V2.
%testEqual(T,V2,V1) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V2 < V1.
%
%contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,intensionalSet,S1), contains(S1,T,V).
%contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,extensional), eValue(E2,intensionalSet,S2), contains(S2,T,V).
%
%contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V).
%
%contains(E,T,VR) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,intensional),
%    eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2),
%    (SR,SO)=((S1,S2);(S2,S1)), contains(SR,T,VR),
%    #false : contains(SO,T,VO), testedEqual(T,VO,VR), VO < VR.
%
%contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
%  eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V),
%  representation(T,intensional).
%contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
%  eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2),
%  representation(T,intensional), testedEqual(T,V1,V2),
%  V=(V1;V2), V=V1 : V1 < V2; V=V2 : V2 < V1.
%
%%%%%%%%%%%%%%%%%% Equality
%
%testEqual(intensionalSet,S1,S2) :- expression(E), E=operation((eq;neq),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2).
%eValue(E,bool,true)  :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedEqual(intensionalSet,S1,S2).
%eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedDifferent(intensionalSet,S1,S2).
%eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedDifferent(intensionalSet,S1,S2).
%eValue(E,bool,false) :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedEqual(intensionalSet,S1,S2).
%
%eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,T2,S2), T2 != intensionalSet.
%eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,T2,S2), T2 != intensionalSet.
%eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,intensionalSet,S2), T1 != intensionalSet.
%eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,intensionalSet,S2), T1 != intensionalSet.
%
%testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V), not contains(S2,T,V), representation(T,extensional).
%testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V), not contains(S1,T,V), representation(T,extensional).
%testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), representation(T,intensional), #false : contains(S2,T,V2), testedEqual(T,V1,V2).
%testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V2), representation(T,intensional), #false : contains(S1,T,V1), testedEqual(T,V1,V2).
%
%testEqual(T,V1,V2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional).
%testedEqual(intensionalSet,V1,V2) :- testEqual(intensionalSet,V1,V2), not testedDifferent(intensionalSet,V1,V2).
%
