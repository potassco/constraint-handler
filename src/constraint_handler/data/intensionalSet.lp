eValue(E,intensionalSet,E) :- expression(E), E=operation((makeSet;union;inter),L).

eValue(E,int,L) :- expression(E), E=operation(length,(S,())), eValue(S,intensionalSet,SR),
    L = #count { V,T : contains(SR,T,V) }.

%%%%%%%%%%%%%%%%% Handling variables

eValue(E,intensionalSet,E) :- E=variable(X), compileAssignToSet(NAME,X,E1).
contains(E,T,V)    :- E=variable(X), compileAssignToSet(NAME,X,E1), eValue(E1,T,V), representation(T,extensional).
precontains(E,T,V) :- E=variable(X), compileAssignToSet(NAME,X,E1), eValue(E1,T,V), representation(T,intensional).

valueInSet(X,T,V) :- eValue(EV,intensionalSet,E), contains(E,T,V), EV=variable(X).

%%%%%%%%%%%%%%%%% Extensional

contains(E,T,V) :- expression(E), E=operation(makeSet,L), E1=@pythonListElements(L), eValue(E1,T,V), representation(T,extensional).

contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V), representation(T,extensional).
contains(E,T,V) :- expression(E), E=operation(union,L), L=(E1,(E2,())), eValue(E2,intensionalSet,S2), contains(S2,T,V), representation(T,extensional).

contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V), representation(T,extensional).

eValue(E,bool,true)  :- expression(E), E=operation(isin,L), L=(E1,(E2,())), eValue(E1,T,V), eValue(E2,intensionalSet,S),     contains(S,T,V), representation(T,extensional).
eValue(E,bool,false) :- expression(E), E=operation(isin,L), L=(E1,(E2,())), eValue(E1,T,V), eValue(E2,intensionalSet,S), not contains(S,T,V), representation(T,extensional).

eValue(E,bool,true)  :- expression(E), E=operation(notin,L), L=(E1,(E2,())), eValue(E1,T,V), eValue(E2,intensionalSet,S), not contains(S,T,V), representation(T,extensional).
eValue(E,bool,false) :- expression(E), E=operation(notin,L), L=(E1,(E2,())), eValue(E1,T,V), eValue(E2,intensionalSet,S),     contains(S,T,V), representation(T,extensional).

%%%%%%%%%%%%%%%%% Intensional

precontains(E,T,V) :- expression(E), E=operation(makeSet,L), E1=@pythonListElements(L), eValue(E1,T,V), representation(T,intensional).
testEqual(T,V1,V2) :- expression(E), precontains(E,T,V1), precontains(E,T,V2), representation(T,intensional), V1 < V2.
contains(E,T,V1) :- precontains(E,T,V1), representation(T,intensional), #false : precontains(E,T,V2), testedEqual(T,V2,V1).

testEqual(T,V1,V2) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V1 < V2.
testEqual(T,V2,V1) :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), V2 < V1.

%TODO
%contains(E,T,V)    :- expression(E), E=operation((union;inter),L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V),  eValue(E2,intensionalSet,S2), contains(S2,T,V),  representation(T,intensional).
contains(E,T,V1) :- expression(E), E=operation(union,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), contains(S1,T,V1), representation(T,intensional), #false : contains(S2,T,V2), testedEqual(T,V2,V1).
contains(E,T,V2) :- expression(E), E=operation(union,L), L=(E1,(E2,())), eValue(E2,intensionalSet,S2), contains(S2,T,V2), representation(T,intensional), #false : contains(S1,T,V1), testedEqual(T,V1,V2).

contains(E,T,V) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
  eValue(E1,intensionalSet,S1), contains(S1,T,V), eValue(E2,intensionalSet,S2), contains(S2,T,V),
  representation(T,intensional).
contains(E,T,V1) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
  eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2),
  representation(T,intensional), testedEqual(T,V1,V2).
contains(E,T,V2) :- expression(E), E=operation(inter,L), L=(E1,(E2,())),
  eValue(E1,intensionalSet,S1), contains(S1,T,V1), eValue(E2,intensionalSet,S2), contains(S2,T,V2),
  representation(T,intensional), testedEqual(T,V2,V1).
%#show contains/3.

%%%%%%%%%%%%%%%%% Equality

testEqual(T,V1,V2) :- expression(E), precontains(E,T,V1), precontains(E,T,V2), representation(T,intensional), V1 < V2.
testEqual(intensionalSet,V1,V2) :- expression(E), E=operation(eq,L), L=(E1,(E2,())), eValue(E1,intensionalSet,S1), eValue(E2,intensionalSet,S2).
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
%testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), #count { 1 : contains(S2,T,V2), testedEqual(T,V1,V2) } 0, representation(T,intensional).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), representation(T,intensional), #false : contains(S2,T,V2), testedEqual(T,V1,V2).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V2), representation(T,intensional), #false : contains(S1,T,V1), testedEqual(T,V1,V2).

testEqual(T,V1,V2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional), V1 < V2.
testedEqual(intensionalSet,V1,V2) :- testEqual(intensionalSet,V1,V2), not testedDifferent(intensionalSet,V1,V2).


%#show testEqual/3.
%#show testedEqual/3.
%#show testedDifferent/3.

#script(python)

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonListElements(clExpr):
    pL = myClorm.cltopy(clExpr,list[evaluator.Expr])
    #test1 = pL[0]
    #res1 = [myClorm.pytocl(e) for e in pL]
    #print(pL,res1,len(res1))
    #print(f"name= {res1.name}, args= {res1.arguments}")
    return [myClorm.pytocl(e) for e in pL]

def pythonEnumerateElements(clExpr):
    pL = myClorm.cltopy(clExpr,list[evaluator.Expr])
    return [myClorm.pytocl(e) for e in enumerate(pL)]

#end.
