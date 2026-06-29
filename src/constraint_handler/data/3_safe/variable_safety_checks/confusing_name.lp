_variable_strip(X,K,S) :- _variable_exists(sugar,X), (K,S,_,_)=@pythonReify(X).
_variable_name(confusing(keyword),X)  :- _variable_strip(X,function,(assert;assign;if;noop;statement_python;seq2)).
_variable_name(confusing(keyword),X)  :- _variable_strip(X,function,(lambda;operation;python;val;variable)).
_variable_name(confusing(keyword),X)  :- _variable_strip(X,function,(boolDomain;definition;fromFacts;fromList)).
_variable_name(confusing(type),X)     :- _variable_strip(X,function,(none;bool;int;float;string;symbol;set;multimap)).
_variable_name(confusing(operator),X) :- _variable_strip(X,function,S), _operator_declared(S).
_variable_name(confusing(number),X)   :- _variable_strip(X,number,N).

_warning(variable(confusingName),(),(X,REASON)) :- _variable_name(confusing(REASON),X).
