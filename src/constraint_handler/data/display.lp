#show.
#show val(X,T,V) : eValue(variable(X),T,V), representation(T,extensional).

#show val(X,T,IDX) : eValue(variable(X),T,S), T = set, IDX = @pythonIndexTerm(S).
#show has(IDX,T,V) : contains(S,T,V), representation(T,extensional), IDX = @pythonIndexTerm(S).
#show has(IDX,T,IDXV) : contains(S,T,V), T = set, IDX = @pythonIndexTerm(S), IDXV = @pythonIndexTerm(V).

#script(python)

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

globTermIndices = dict()
def pythonIndexTerm(clT):
    #print("pythonIndexTerm",clT)
    pT = myClorm.cltopy(clT,evaluator.Expr)
    #clT = pT
    if clT not in globTermIndices:
        globTermIndices[clT] = len(globTermIndices)
    #else:
    #    print("hello",clT)
    #print(globTermIndices)
    return myClorm.pytocl(globTermIndices[clT])


#end.
