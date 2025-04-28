%%%%%%%%%%%%%%%%% length

computed(length,ARGS,int,N) :- compute(length,ARGS),
    ARGS = (intensionalSet,(SET,())),
    N = #count { V,T : contains(SET,T,V) }.

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

computed(isin,ARGS,bool,true)  :- compute(isin,ARGS), ARGS = (T,(V,(intensionalSet,(S,())))),
    representation(T,extensional),     contains(S,T,V).
computed(isin,ARGS,bool,false) :- compute(isin,ARGS), ARGS = (T,(V,(intensionalSet,(S,())))),
    representation(T,extensional), not contains(S,T,V).
computed(notin,ARGS,bool,false) :- compute(notin,ARGS), ARGS = (T,(V,(intensionalSet,(S,())))),
    representation(T,extensional),     contains(S,T,V).
computed(notin,ARGS,bool,true)  :- compute(notin,ARGS), ARGS = (T,(V,(intensionalSet,(S,())))),
    representation(T,extensional), not contains(S,T,V).


testEqual(T,V1,V2)  :- compute((isin;notin),ARGS), ARGS = (T,(V1,(intensionalSet,(S,())))),
    representation(T,intensional),     contains(S,T,V2).

computed(isin,ARGS,bool,true)   :- compute(isin,ARGS), ARGS = (T,(V1,(intensionalSet,(S,())))),
    representation(T,intensional),     contains(S,T,V2), testedEqual(T,V1,V2).
computed(isin,ARGS,bool,false)  :- compute(isin,ARGS), ARGS = (T,(V1,(intensionalSet,(S,())))),
    representation(T,intensional),     #false : contains(S,T,V2), testedEqual(T,V1,V2).
computed(notin,ARGS,bool,false) :- compute(isin,ARGS), ARGS = (T,(V1,(intensionalSet,(S,())))),
    representation(T,intensional),     contains(S,T,V2), testedEqual(T,V1,V2).
computed(notin,ARGS,bool,true)  :- compute(isin,ARGS), ARGS = (T,(V1,(intensionalSet,(S,())))),
    representation(T,intensional),     #false : contains(S,T,V2), testedEqual(T,V1,V2).

%%%%%%%%%%%%%%%%% makeSet

computed(makeSet,ARGS,intensionalSet,makeSet(ARGS)) :- compute(makeSet,ARGS).
testEqual(T,V1,V2) :- compute(makeSet,ARGS),
    (T,V1)=@pythonListElements(ARGS,2), (T,V2)=@pythonListElements(ARGS,2),
    representation(T,intensional), V1 < V2.
contains(makeSet(ARGS),T,V) :- compute(makeSet,ARGS),
    (T,V)=@pythonListElements(ARGS,2), representation(T,extensional).
contains(makeSet(ARGS),T,V1) :- compute(makeSet,ARGS), representation(T,intensional),
    (T,V1)=@pythonListElements(ARGS,2),
    #false : (T,V2)=@pythonListElements(ARGS,2), testedEqual(T,V2,V1), V2 < V1.

%%%%%%%%%%%%%%%%% union inter

testEqual(T,VSMALL,VBIG) :- compute((union;inter),ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional), (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL < VBIG.

computed(union,ARGS,intensionalSet,union(ARGS))   :- compute(union,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))).
contains(union(ARGS),T,V) :- compute(union,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    representation(T,extensional), contains((S1;S2),T,V).

contains(union(ARGS),T,VR) :- compute(union,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    representation(T,intensional),
    (SR,SO)=((S1,S2);(S2,S1)), contains(SR,T,VR),
    #false : contains(SO,T,VO), testedEqual(T,VO,VR), VO < VR.

computed(inter,ARGS,intensionalSet,inter(ARGS))   :- compute(inter,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))).
contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    representation(T,extensional), contains(S1,T,V), contains(S2,T,V).

contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    representation(T,intensional),
    contains(S1,T,V), contains(S2,T,V).
contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    representation(T,intensional),
    contains(S1,T,V1), contains(S2,T,V2), testedEqual(T,V1,V2),
    V=(V1;V2), V=V1 : V1 < V2; V=V2 : V2 < V1.

%%%%%%%%%%%%%%%%% Equality

testEqual(intensionalSet,S1,S2) :- compute((eq;neq),ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))).
computed(eq,ARGS,bool,true)   :- compute(eq,ARGS),  ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))), testedEqual(intensionalSet,S1,S2).
computed(eq,ARGS,bool,false)  :- compute(eq,ARGS),  ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))), testedDifferent(intensionalSet,S1,S2).
computed(neq,ARGS,bool,true)  :- compute(neq,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))), testedDifferent(intensionalSet,S1,S2).
computed(neq,ARGS,bool,false) :- compute(neq,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))), testedEqual(intensionalSet,S1,S2).

computed(eq,ARGS,bool,false) :- compute(eq,ARGS),  ARGS = (intensionalSet,(S1,(T2,(S2,())))), T2 != intensionalSet.
computed(eq,ARGS,bool,false) :- compute(eq,ARGS),  ARGS = (T1,(S1,(intensionalSet,(S2,())))), T1 != intensionalSet.
computed(neq,ARGS,bool,true) :- compute(neq,ARGS), ARGS = (intensionalSet,(S1,(T2,(S2,())))), T2 != intensionalSet.
computed(neq,ARGS,bool,true) :- compute(neq,ARGS), ARGS = (T1,(S1,(intensionalSet,(S2,())))), T1 != intensionalSet.

testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V), not contains(S2,T,V), representation(T,extensional).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V), not contains(S1,T,V), representation(T,extensional).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), representation(T,intensional), #false : contains(S2,T,V2), testedEqual(T,V1,V2).
testedDifferent(intensionalSet,S1,S2) :- testEqual(intensionalSet,S1,S2), contains(S2,T,V2), representation(T,intensional), #false : contains(S1,T,V1), testedEqual(T,V1,V2).

testEqual(T,V1,V2) :- testEqual(intensionalSet,S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional).
testedEqual(intensionalSet,V1,V2) :- testEqual(intensionalSet,V1,V2), not testedDifferent(intensionalSet,V1,V2).

%%%%%%%%%%%%%%%%% Subset

_set_testSubset(S1,S2) :- compute(subset,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))).
_set_testedNonSubset(S1,S2) :- _set_testSubset(S1,S2), contains(S1,T,V), representation(T,extensional), not contains(S2,T,V).
testEqual(T,V1,V2) :- testSubset(S1,S2), contains(S1,T,V1), contains(S2,T,V2), representation(T,intensional).
_set_testedNonSubset(S1,S2) :- _set_testSubset(S1,S2), contains(S1,T,V1), representation(T,intensional),
    #false : contains(S2,T,V2), testedEqual(T,V1,V2).

computed(subset,ARGS,bool,true)  :- compute(subset,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    not _set_testedNonSubset(S1,S2).
computed(subset,ARGS,bool,false) :- compute(subset,ARGS), ARGS = (intensionalSet,(S1,(intensionalSet,(S2,())))),
    _set_testedNonSubset(S1,S2).
computed(subset,ARGS,bool,false) :- compute(subset,ARGS), ARGS = (T1,(S1,(T2,(S2,())))),
    (T1;T2) != intensionalSet, (T1;T2) = intensionalSet.

#script(python)

import itertools
import clingo

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonReversed(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    pRL = list(reversed(pL))
    return myClorm.pytocl(pRL)

def pythonListElements(clExpr,clBatchSize = clingo.Number(1)):
    pBatchSize = myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    if pBatchSize == 1:
        pGroups = pL
    else:
        pGroups = itertools_batched(pL,pBatchSize)
    return [myClorm.pytocl(e) for e in pGroups]


def pythonEnumerateElements(clExpr):
    pL = myClorm.cltopy(clExpr,list[evaluator.Expr])
    return [myClorm.pytocl(e) for e in enumerate(pL)]

# https://docs.python.org/3/library/itertools.html#itertools.batched
def prepython12_itertools_batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError('batched(): incomplete batch')
        yield batch

itertools_batched = itertools.batched if hasattr(itertools,'batched') else prepython12_itertools_batched

#end.
