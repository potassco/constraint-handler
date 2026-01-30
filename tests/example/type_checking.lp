%%% Setup
variable_declare(check, v(int), fromFacts).
variable_domain(v(int), val(int,1..3)).
variable_declare(check, v(float), fromFacts).
variable_domain(v(float), val(float,float(1..3))).
variable_declare(check, v(str), fromFacts).
variable_domain(v(str), val(str, "some_string")).
variable_declare(check, v(bool), boolDomain).
variable_declare(check, v(symbol), fromFacts).
variable_domain(v(symbol), val(symbol, some_symbol)).
variable_define(check, v(none), val(none,none)).
set_declare(check, v(set)).
1 { selected_S(S) : S=1..3 } 1.
set_assign(check, v(set), val(int, S*V)) :- selected_S(S), V=1..3.
multimap_declare(check, v(multimap)).
1 { selected_M(M) : M=1..3 } 1.
multimap_assign(check, v(multimap), val(int, K), val(int, M*K*V)) :- selected_M(M), K=1..3,V=1..3.

% Conditionals
variable_define(types, cond(T,OP), operation(OP, (variable(v(T)),()))) :- _type(T), OP = hasValue.
failed(hasValue) :- warning(type(failed_operation),(),(_,hasValue,_)).