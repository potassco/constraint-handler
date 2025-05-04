#defined set_declare/2.
#defined set_assign/3.

representation(set,intensional).

%%%%%%%%%%%%%%%%% length

computed(length,ARGS,int,N) :- compute(length,ARGS),
    ARGS = (set,(SET,())),
    N = #count { V,T : _set_contains(SET,T,V) }.

%%%%%%%%%%%%%%%%% assignToSet set_value

%representation(multimap,intensional).
%_set_add(E,EK) :- set_assign(CNAME,X,EK), engine(CNAME,compile), E = variable(X).

eValue(EX,set,EX) :- EX=variable(X), set_declare(NAME,X).
%eValue(EX,set,EX) :- EX=variable(X), _set_compileAssign(NAME,X,E1).
_set_contains(E,T,V)    :- E=variable(X), representation(T,extensional), _set_compileAssign(NAME,X,E1), eValue(E1,T,V).

compute(eq,(T,(V1,(T,(V2,()))))) :- E=variable(X), representation(T,intensional),
    _set_compileAssign(N1,X,E1), eValue(E1,T,V1),
    _set_compileAssign(N2,X,E2), eValue(E2,T,V2), V1 < V2.
_set_contains(E,T,V1) :- E=variable(X), representation(T,intensional),
    _set_compileAssign(NAME,X,E1), eValue(E1,T,V1),
    #false : _set_compileAssign(N2,X,E2), eValue(E2,T,V2), computed(eq,(T,(V2,(T,(V1,())))),bool,true), V2 < V1.

set_value(X,T,V) :- eValue(EV,set,E), _set_contains(E,T,V), EV=variable(X).

%%%%%%%%%%%%%%%%% isin notin

computed(isin,ARGS,bool,true)  :- compute(isin,ARGS), ARGS = (T,(V,(set,(S,())))),
    representation(T,extensional),     _set_contains(S,T,V).
computed(isin,ARGS,bool,false) :- compute(isin,ARGS), ARGS = (T,(V,(set,(S,())))),
    representation(T,extensional), not _set_contains(S,T,V).
computed(notin,ARGS,bool,false) :- compute(notin,ARGS), ARGS = (T,(V,(set,(S,())))),
    representation(T,extensional),     _set_contains(S,T,V).
computed(notin,ARGS,bool,true)  :- compute(notin,ARGS), ARGS = (T,(V,(set,(S,())))),
    representation(T,extensional), not _set_contains(S,T,V).

compute(eq,(T,(V1,(T,(V2,())))))  :- compute((isin;notin),ARGS), ARGS = (T,(V1,(set,(S,())))),
    representation(T,intensional), _set_contains(S,T,V2).

computed(isin,ARGS,bool,true)   :- compute(isin,ARGS), ARGS = (T,(V1,(set,(S,())))),
    representation(T,intensional),     _set_contains(S,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).
computed(isin,ARGS,bool,false)  :- compute(isin,ARGS), ARGS = (T,(V1,(set,(S,())))),
    representation(T,intensional),     #false : _set_contains(S,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).
computed(notin,ARGS,bool,false) :- compute(isin,ARGS), ARGS = (T,(V1,(set,(S,())))),
    representation(T,intensional),     _set_contains(S,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).
computed(notin,ARGS,bool,true)  :- compute(isin,ARGS), ARGS = (T,(V1,(set,(S,())))),
    representation(T,intensional),     #false : _set_contains(S,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).

%%%%%%%%%%%%%%%%% makeSet

computed(makeSet,ARGS,set,makeSet(ARGS)) :- compute(makeSet,ARGS).
compute(eq,(T,(V1,(T,(V2,()))))) :- compute(makeSet,ARGS),
    (T,V1)=@pythonListElements(ARGS,2), (T,V2)=@pythonListElements(ARGS,2),
    representation(T,intensional), V1 < V2.
_set_contains(makeSet(ARGS),T,V) :- compute(makeSet,ARGS),
    (T,V)=@pythonListElements(ARGS,2), representation(T,extensional).
_set_contains(makeSet(ARGS),T,V1) :- compute(makeSet,ARGS), representation(T,intensional),
    (T,V1)=@pythonListElements(ARGS,2),
    #false : (T,V2)=@pythonListElements(ARGS,2), computed(eq,(T,(V2,(T,(V1,())))),bool,true), V2 < V1.

%%%%%%%%%%%%%%%%% union inter

compute(eq,(T,(VSMALL,(T,(VBIG,()))))) :- compute((union;inter),ARGS), ARGS = (set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional), (VSMALL,VBIG)=((V1,V2);(V2,V1)), VSMALL < VBIG.

computed(union,ARGS,set,union(ARGS))   :- compute(union,ARGS), ARGS = (set,(S1,(set,(S2,())))).
_set_contains(union(ARGS),T,V) :- compute(union,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    representation(T,extensional), _set_contains((S1;S2),T,V).

_set_contains(union(ARGS),T,VR) :- compute(union,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    representation(T,intensional),
    (SR,SO)=((S1,S2);(S2,S1)), _set_contains(SR,T,VR),
    #false : _set_contains(SO,T,VO), computed(eq,(T,(VO,(T,(VR,())))),bool,true), VO < VR.

computed(inter,ARGS,set,inter(ARGS))   :- compute(inter,ARGS), ARGS = (set,(S1,(set,(S2,())))).
_set_contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    representation(T,extensional), _set_contains(S1,T,V), _set_contains(S2,T,V).

_set_contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    representation(T,intensional),
    _set_contains(S1,T,V), _set_contains(S2,T,V).
_set_contains(inter(ARGS),T,V) :- compute(inter,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    representation(T,intensional),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true),
    V=(V1;V2), V=V1 : V1 < V2; V=V2 : V2 < V1.

%%%%%%%%%%%%%%%%% Equality
compute(eq,ARGS) :- compute(neq,ARGS), ARGS = (T1,(S1,(T2,(S2,())))), (T1;T2)=set.
computed(neq,ARGS,bool,NEQ) :- computed(eq,ARGS,bool,EQ), ARGS = (T1,(S1,(T2,(S2,())))), (T1;T2)=set, (EQ,NEQ)=((true,false);(false,true)).

computed(eq,ARGS,bool,true)   :- compute(eq,ARGS),  ARGS = (set,(S1,(set,(S2,())))), not computed(eq,ARGS,bool,false).

computed(eq,ARGS,bool,false) :- compute(eq,ARGS),  ARGS = (set,(S1,(T2,(S2,())))), T2 != set.
computed(eq,ARGS,bool,false) :- compute(eq,ARGS),  ARGS = (T1,(S1,(set,(S2,())))), T1 != set.

computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS=(set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V), not _set_contains(S2,T,V), representation(T,extensional).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS=(set,(S1,(set,(S2,())))),
    _set_contains(S2,T,V), not _set_contains(S1,T,V), representation(T,extensional).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS=(set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V1), representation(T,intensional),
    #false : _set_contains(S2,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).
computed(eq,ARGS,bool,false) :- compute(eq,ARGS), ARGS=(set,(S1,(set,(S2,())))),
    _set_contains(S2,T,V2), representation(T,intensional),
    #false : _set_contains(S1,T,V1), computed(eq,(T,(V1,(T,(V2,())))),bool,true).

compute(eq,(T,(V1,(T,(V2,()))))) :- compute(eq,ARGS), ARGS=(set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional).

%%%%%%%%%%%%%%%%% Equality axioms

:- computed(eq,(set,(X,(set,(X,())))),bool,false). %%% reflexivity
:-  computed(eq,(set,(X,(set,(Y,())))),bool,true),
    computed(eq,(set,(Y,(set,(X,())))),bool,false). %%% symmetry
:-  computed(eq,(set,(L1,(set,(R1,())))),bool,true),
    computed(eq,(set,(L2,(set,(R2,())))),bool,true),
    computed(eq,(set,(L3,(set,(R3,())))),bool,false),
    X=(L1;R1), Y=(L1;R1),
    Y=(L2;R2), Z=(L2;R2),
    X=(L3;R3), Z=(L3;R3),
    X != Y, Y !=Z, X != Z. %%% transitivity

%%%%%%%%%%%%%%%%% Subset

compute(eq,(T,(V1,(T,(V2,()))))) :- compute(subset,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V1), _set_contains(S2,T,V2), representation(T,intensional).
computed(subset,ARGS,bool,false) :- compute(subset,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V), representation(T,extensional), not _set_contains(S2,T,V).
computed(subset,ARGS,bool,false) :- compute(subset,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    _set_contains(S1,T,V1), representation(T,intensional),
    #false : _set_contains(S2,T,V2), computed(eq,(T,(V1,(T,(V2,())))),bool,true).

computed(subset,ARGS,bool,true)  :- compute(subset,ARGS), ARGS = (set,(S1,(set,(S2,())))),
    not computed(subset,ARGS,bool,false).
computed(subset,ARGS,bool,false) :- compute(subset,ARGS), ARGS = (T1,(S1,(T2,(S2,())))),
    (T1;T2) != set, (T1;T2) = set.

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


def pythonEnumerateElements(clExpr,clBatchSize = clingo.Number(1)):
    pBatchSize = myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    if pBatchSize == 1:
        pGroups = pL
    else:
        pGroups = itertools_batched(pL,pBatchSize)
    return [myClorm.pytocl(e) for e in enumerate(pGroups)]

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
