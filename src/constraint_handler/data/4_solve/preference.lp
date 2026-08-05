#defined preference_maximizeScore/0.

_warning(preference(unsupported),LBL1,("multiple scores for the same expression",E,K1,K2)) :- _passed(sugar,LBL1,preference_holds(E,K1)), _passed(sugar,LBL2,preference_holds(E,K2)), K1 < K2.


_preference_expression(E) :- _preference_expressionScore(E,K).

_preference_index(E,0) :- _preference_expression(E), #count { F : _preference_expression(F), F < E } = 0.
_preference_index(F,IDX+1) :- _preference_index(E,IDX), _preference_expression(F), E < F,
    #count { G : _preference_expression(G), E < G, G < F } = 0.

_preference_potentialAux(0,0) :- preference_maximizeScore.
_preference_potentialAux(IDX+1,W)   :- _preference_potentialAux(IDX,W), _preference_index(E,IDX).
_preference_potentialAux(IDX+1,W+K) :- _preference_potentialAux(IDX,W), _preference_index(E,IDX), _preference_expressionScore(E, K), K > 0.
_preference_potentialScore(W) :- _preference_potentialAux(IDX,W), not _preference_potentialAux(IDX+1,W).
preference_score(W) :- preference_maximizeScore, W = #sum { K,E : _shared_value(E,val(bool,true)),  _preference_expressionScore(E,K), K > 0 }.

#heuristic _shared_value(E,val(bool,true)) : _preference_expressionScore(E,K). [1,true]
#heuristic preference_score(W) : _preference_potentialScore(W),W>0. [1+W,true]
