%%% Test set_declare_from/2 with fromList and fromFacts
%%%
%%% s has base domain {1, 2, 3} (via fromList)
%%% Constrained: 1 and 2 must be in s
%%% => s always contains 1 and 2; 3 is optional
%%%
%%% t has base domain {red, green, blue} (via fromFacts + set_base_domain)
%%% Constrained: red must be in t
%%% => t always contains red; green and blue are optional

set_declare_from(s, fromList((val(int,1),(val(int,2),(val(int,3),()))))).
ensure(operation(isin,(val(int,1),(variable(s),())))).
ensure(operation(isin,(val(int,2),(variable(s),())))).

set_declare_from(t, fromFacts).
set_base_domain(t, val(symbol,(red;green;blue))).
ensure(operation(isin,(val(symbol,red),(variable(t),())))).
