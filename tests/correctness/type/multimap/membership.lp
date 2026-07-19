phase_request(type_check,true).

variable_declare(v(int),fromFacts).
variable_domain(v(int),val(int,3)).
variable_declare(v(float),fromFacts).
variable_domain(v(float),val(float,float("3.14"))).
variable_declare(v(string),fromFacts).
variable_domain(v(string),val(string,"s")).
variable_declare(v(bool),boolDomain).
variable_declare(v(symbol),fromFacts).
variable_domain(v(symbol),val(symbol,some_symbol)).

variable_declare(v(multimap),multimap).
multimap_assign(v(multimap),variable(v(symbol)),variable(v(int))).

check_types(T) :- variable_declare(v(T),_).

variable_define(check(OP,multimap), EXPR) :-
    EXPR = operation(OP,(variable(v(T)),(variable(v(multimap)),()))),
    check_types(T),
    OP = (multimap_isin;find).
