_variable_confusingName((assert;assign;if;noop;statement_python;seq2),keyword).
_variable_confusingName((lambda;operation;python;val;variable),keyword).
_variable_confusingName((boolDomain;fromFacts;fromList),keyword).
_variable_confusingName((none;bool;int;float;string;symbol;set;multimap),type).
_variable_confusingName(O,operator) :- _operator_declared(O).

_warning(variable(confusingName),(),(X,REASON)) :- _variable_exists(sugar,X), _variable_confusingName(BAD,REASON), (function,BAD,N,ARGS)=@pythonReify(X).
_warning(variable(confusingName),(),(X,number)) :- _variable_exists(sugar,X), (number,_,_,_)=@pythonReify(X).
