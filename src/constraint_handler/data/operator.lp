
_operator_declared(O) :- operator_declare(O,_,_).
_operator_declared(O) :- operator_declare_variadic(O,_,_,_).
_operator_safe(O) :- _operator_declared(O), not _operator_unsafe(O).
