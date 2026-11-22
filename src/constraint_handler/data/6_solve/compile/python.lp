_python_evaluated(Q,M,RES) :- _python_evaluate(Q,E,M), RES=@pythonEvalExpr(E,M,ID), _main_solverIdentifiers(ID).
_python_result(E,V) :- _python_evaluated(E,M,valid(V)).
_python_result(E,bad) :- _python_evaluated(E,M,error(KIND,MSG)).
_warning(KIND,(),(python,E,MSG)) :- _python_evaluated(E,M,error(KIND,MSG)).

_direct_explode(V) :- _python_result(E,V).
_se_value(E,V) :- _python_result(E,V), V=(bad;val(T,W)).
_se_value(E,V) :- _python_result(E,RV), _expression_tupleLength(implode,RV,N), _direct_exploded(RV,V).
_se_value(E,ref(set,E)) :- _python_result(E,set(L)).
_set_candidate(E,V) :- _python_result(E,set(L)), RV=@pythonListElements(L), _direct_exploded(RV,V).
_direct_imploded(ref(set,E),set(L)) :- _python_result(E,set(L)).
