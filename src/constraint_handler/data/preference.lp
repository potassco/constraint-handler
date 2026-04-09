#defined preference_maximizeScore/0.

_warning(preference(unsupported),(),("multiple scores for the same expression",E,K,L)) :- _preference_expressionScore(E,K), _preference_expressionScore(E,L), K < L.


_preference_expressionScore(operation(eq,(variable(X),(E,()))), K) :- preference_variableValue(CNAME,X,E,K), K > 0.
_preference_expressionScore(operation(wnot,(operation(eq,(variable(X),(E,()))),())),-K) :- preference_variableValue(CNAME,X,E,K), K < 0.

_preference_expressionScore(E, K) :- preference_holds(CNAME,E,K), K > 0.
_preference_expressionScore(operation(wnot,(E,())),-K) :- preference_holds(CNAME,E,K), K < 0.

_preference_expression(E) :- _preference_expressionScore(E,K).
direct_query(E) :- _preference_expression(E).

_preference_index(E,0) :- _preference_expression(E), #count { F : _preference_expression(F), F < E } = 0.
_preference_index(F,IDX+1) :- _preference_index(E,IDX), _preference_expression(F), E < F,
    #count { G : _preference_expression(G), E < G, G < F } = 0.

_preference_potentialAux(0,0) :- preference_maximizeScore.
_preference_potentialAux(IDX+1,W)   :- _preference_potentialAux(IDX,W), _preference_index(E,IDX).
_preference_potentialAux(IDX+1,W+K) :- _preference_potentialAux(IDX,W), _preference_index(E,IDX), _preference_expressionScore(E, K), K > 0.
_preference_potentialScore(W) :- _preference_potentialAux(IDX,W), not _preference_potentialAux(IDX+1,W).
preference_score(W) :- preference_maximizeScore, W = #sum { K,E : _se_value(E,val(bool,true)),  _preference_expressionScore(E, K), K > 0 }.

#heuristic _se_value(E,val(bool,true)) : _preference_expressionScore(E,K). [1,true]
#heuristic preference_score(W) : _preference_potentialScore(W),W>0. [1+W,true]
