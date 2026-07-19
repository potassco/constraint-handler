phase_request(type_check,true).

variable_declare(v(int),fromFacts).
variable_domain(v(int),val(int,3)).
variable_declare(v(float),fromFacts).
variable_domain(v(float),val(float,float("3.14"))).
variable_declare(v(string),fromFacts).
variable_domain(v(string),val(string,"s")).
variable_declare(v(bool),boolDomain).

variable_declare(v(set),set).
set_assign(v(set),variable(v(int))).
set_assign(v(set),variable(v(bool))).
set_baseDomain(v(set),val(float,float("2.71"))).
set_baseDomain(v(set),val(string,"x")).

check_types(int;float;string;bool).

variable_define(check(OP,set), EXPR) :-
    EXPR = operation(OP,(variable(v(T)),(variable(v(set)),()))),
    check_types(T),
    OP = (set_isin;set_notin).
