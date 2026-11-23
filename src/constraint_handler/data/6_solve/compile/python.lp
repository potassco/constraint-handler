_python_evaluate(E) :- _python_request(Q,E).
_python_evaluate(E) :- _python_evaluate(E,()).
_python_cached(E,ID,RES) :- _python_evaluate(E), _main_solverIdentifiers(ID), RES=@pythonEvalExpr(E,(),ID).
_python_evaluated(Q,RES) :- _python_request(Q,E), _python_cached(E,ID,RES).
_python_evaluated(E,RES) :- _python_evaluate(E,()), _python_cached(E,ID,RES).
_python_evaluated(E,RES) :- _python_evaluate(E,(BINDING,REST)), _main_solverIdentifiers(ID), RES=@pythonEvalExpr(E,(BINDING,REST),ID).
_python_evaluated(E,valid(bad)) :- _python_evaluated(E,error(KIND,MSG)).
_warning(KIND,(),(python,E,MSG)) :- _python_evaluated(E,error(KIND,MSG)).

_direct_explode(V) :- _python_evaluated(E,valid(V)).
_se_value(E,V) :- _python_evaluated(E,valid(V)), V=(bad;val(T,W)).
_se_value(E,V) :- _python_evaluated(E,valid(RV)), _expression_tupleLength(implode,RV,N), _direct_exploded(RV,V).
_se_value(E,ref(set,E)) :- _python_evaluated(E,valid(set(L))).
_set_candidate(E,V) :- _python_evaluated(E,valid(set(L))), _set_contains(set(L),V).
_direct_imploded(ref(set,E),set(L)) :- _python_evaluated(E,valid(set(L))).
