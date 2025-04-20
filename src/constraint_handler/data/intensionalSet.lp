eValue(E,intensionalSet,E) :- expression(E), E=operation((makeSet;union;inter),L).

eValue(E,int,L) :- expression(E), E=operation(length,(S,())), eValue(S,intensionalSet,SR),
    L = #count { V,T : contains(SR,T,V) }.

%%%%%%%%%%%%%%%%% assignToSet valueInSet

eValue(E,intensionalSet,E) :- E=variable(X), compileAssignToSet(NAME,X,E1).
contains(E,T,V)    :- E=variable(X), representation(T,extensional), compileAssignToSet(NAME,X,E1), eValue(E1,T,V).

testEqual(T,V1,V2) :- E=variable(X), representation(T,intensional),
    compileAssignToSet(N1,X,E1), eValue(E1,T,V1),
    compileAssignToSet(N2,X,E2), eValue(E2,T,V2), V1 < V2.
contains(E,T,V1) :- E=variable(X), representation(T,intensional),
    compileAssignToSet(NAME,X,E1), eValue(E1,T,V1),
    #false : compileAssignToSet(N2,X,E2), eValue(E2,T,V2), testedEqual(T,V2,V1), V2 < V1.

valueInSet(X,T,V) :- eValue(EV,intensionalSet,E), contains(E,T,V), EV=variable(X).

%%%%%%%%%%%%%%%%% isin notin

eValue(E,bool,true)  :- expression(E), E=operation(isin,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,T,V), eValue(E2,intensionalSet,S),     contains(S,T,V).
eValue(E,bool,false) :- expression(E), E=operation(isin,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,T,V), eValue(E2,intensionalSet,S), not contains(S,T,V).

testEqual(T,V1,V2)   :- expression(E), E=operation(isin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S),     contains(S,T,V2).
eValue(E,bool,true)  :- expression(E), E=operation(isin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S), contains(S,T,V2), testedEqual(T,V1,V2).
eValue(E,bool,false) :- expression(E), E=operation(isin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S), #false : contains(S,T,V2), testedEqual(T,V1,V2).


eValue(E,bool,true)  :- expression(E), E=operation(notin,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,T,V), eValue(E2,intensionalSet,S), not contains(S,T,V).
eValue(E,bool,false) :- expression(E), E=operation(notin,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,T,V), eValue(E2,intensionalSet,S),     contains(S,T,V).

testEqual(T,V1,V2)   :- expression(E), E=operation(notin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S),     contains(S,T,V2).
eValue(E,bool,false) :- expression(E), E=operation(notin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S), contains(S,T,V2), testedEqual(T,V1,V2).
eValue(E,bool,true)  :- expression(E), E=operation(notin,L), L=(E1,(E2,())), representation(T,intensional), eValue(E1,T,V1), eValue(E2,intensionalSet,S), #false : contains(S,T,V2), testedEqual(T,V1,V2).

%%%%%%%%%%%%%%%%% makeSet

contains(E,T,V) :- expression(E), E=operation(makeSet,L), representation(T,extensional),
    E1=@pythonListElements(L), eValue(E1,T,V).
testEqual(T,V1,V2) :- expression(E), E=operation(makeSet,L), representation(T,intensional),
    E1=@pythonListElements(L), eValue(E1,T,V1),
    E2=@pythonListElements(L), eValue(E2,T,V2), V1 < V2.
contains(E,T,V1) :- expression(E), E=operation(makeSet,L), representation(T,intensional),
    E1=@pythonListElements(L), eValue(E1,T,V1),
    #false : E2=@pythonListElements(L), eValue(E2,T,V2), testedEqual(T,V2,V1), V2 < V1.

%%%%%%%%%%%%%%%%% union inter

testEqual(T,V1,V2) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V1 < V2.
testEqual(T,V2,V1) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V2 < V1.

contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,intensionalSet,S1), contains(S1,T,V).
contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,extensional), eValue(E2,intensionalSet,S2), contains(S2,T,V).

contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())), representation(T,extensional), eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V).

contains(E,T,VR) :- expression(E), E=operation(union,L), L=(E1,(E2,())), representation(T,intensional),
    eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2),
    (SR,SO)=((S1,S2);(S2,S1)), contains(SR,T,VR),
    #false : contains(SO,T,VO), testedEqual(T,VO,VR), VO < VR.

contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
  eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V),
  representation(T,intensional).
contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
  eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2),
  representation(T,intensional), testedEqual(T,V1,V2),
  V=(V1;V2), V=V1 : V1 < V2; V=V2 : V2 < V1.

%%%%%%%%%%%%%%%%% Equality

testEqual(intensionalSet,S1,S2) :- expression(E), E=operation((eq;neq),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2).
eValue(E,bool,true)  :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedEqual(intensionalSet,S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedDifferent(intensionalSet,S1,S2).
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedDifferent(intensionalSet,S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2), testedEqual(intensionalSet,S1,S2).

eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,T2,S2), T2 != intensionalSet.
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,T2,S2), T2 != intensionalSet.
eValue(E,bool,false) :- expression(E), E=operation(eq,L),  L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,intensionalSet,S2), T1 != intensionalSet.
eValue(E,bool,true)  :- expression(E), E=operation(neq,L), L=(E1,(E2,())), eValue(E1,T1,S1), eValue(E2,intensionalSet,S2), T1 != intensionalSet.

testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V), not contains(S2,T,V), representation(T,extensional).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V), not contains(S1,T,V), representation(T,extensional).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), representation(T,intensional), #false : contains(S2,T,V2), testedEqual(T,V1,V2).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V2), representation(T,intensional), #false : contains(S1,T,V1), testedEqual(T,V1,V2).

testEqual(T,V1,V2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional).
testedEqual(intensionalSet,V1,V2) :- testEqual(intensionalSet,V1,V2), not testedDifferent(intensionalSet,V1,V2).

%%%%%%%%%%%%%%%%% Subset

testSubset(S1,S2) :- expression(E), E=operation(subset,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2).
testedNonSubset(S1,S2) :- testSubset(S1,S2), contains(S1,T,V), representation(T,extensional), not contains(S2,T,V).
testEqual(T,V1,V2) :- testSubset(S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional).
testedNonSubset(S1,S2) :- testSubset(S1,S2), contains(S1,T,V1), representation(T,intensional),
    #false : contains(S2,T,V2), testedEqual(T,V1,V2).

eValue(E,bool,true)  :- expression(E), E=operation(subset,L), L=(E1,(E2,())),
    eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2),
    not testedNonSubset(S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(subset,L), L=(E1,(E2,())),
    eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2),
    testedNonSubset(S1,S2).
eValue(E,bool,false) :- expression(E), E=operation(subset,L), L=(E1,(E2,())),
    eValue(E1,T1,S1), eValue(E2,T2,S2), (T1;T2) != intensionalSet, (T1;T2) = intensionalSet.

#script(python)

import itertools
import clingo

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonListElements(clExpr,clBatchSize = clingo.Number(1)):
    pBatchSize = myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list[evaluator.Expr])
    if pBatchSize == 1:
        pGroups = pL
    else:
        pGroups = itertools.batched(pL,pBatchSize)
    return [myClorm.pytocl(e) for e in pGroups]


def pythonEnumerateElements(clExpr):
    pL = myClorm.cltopy(clExpr,list[evaluator.Expr])
    return [myClorm.pytocl(e) for e in enumerate(pL)]

#end.
