#defined preference_holds/2.
#defined preference_holds/3.
#defined preference_variableValue/2.
#defined preference_variableValue/3.
#defined preference_maximizeScore/0.

warning((unsupported,"multiple scores for the same expression",E,K,L)) :- _preference_expressionScore(E,K), _preference_expressionScore(E,L), K < L.

%%% convenience
preference_variableValue(CNAME,X,E,1) :- preference_variableValue(CNAME,X,E).
preference_holds(CNAME,E,1) :- preference_holds(CNAME,E).

_preference_expressionScore(EQ, K) :- preference_variableValue(CNAME,X,E,K), K > 0, EQ = operation(eq,(variable(X),(E,()))).
_preference_expressionScore(NE,-K) :- preference_variableValue(CNAME,X,E,K), K < 0,
    EQ = operation(eq,(variable(X),(E,()))),
    NE = operation(wnot,(EQ,())).

_preference_expressionScore(E, K) :- preference_holds(CNAME,E,K), K > 0.
_preference_expressionScore(F,-K) :- preference_holds(CNAME,E,K), K < 0,
    F = operation(wnot,(E,())).

_preference_expression(E) :- _preference_expressionScore(E,K).
direct_query(E) :- _preference_expression(E).

_preference_index(E,0) :- _preference_expression(E), #count { F : _preference_expression(F), F < E } = 0.
_preference_index(F,IDX+1) :- _preference_index(E,IDX), _preference_expression(F), E < F,
    #count { G : _preference_expression(G), E < G, G < F } = 0.

_preference_potentialAux(0,0) :- preference_maximizeScore.
_preference_potentialAux(IDX+1,W)   :- _preference_potentialAux(IDX,W), _preference_index(E,IDX).
_preference_potentialAux(IDX+1,W+K) :- _preference_potentialAux(IDX,W), _preference_index(E,IDX), _preference_expressionScore(E, K), K > 0.
_preference_potentialScore(W) :- _preference_potentialAux(IDX,W), not _preference_potentialAux(IDX+1,W).
preference_score(W) :- preference_maximizeScore, W = #sum { K,E : eValue(E,bool,true),  _preference_expressionScore(E, K), K > 0 }.

#heuristic eValue(E,bool,true) : _preference_expressionScore(E,K). [1,true]
#heuristic preference_score(W) : _preference_potentialScore(W),W>0. [1+W,true]
