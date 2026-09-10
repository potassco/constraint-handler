%%% bool_evaluate integration checks (success and failure forms)

variable_declare(b,boolDomain).
variable_declare(c,boolDomain).

bool_evaluate(operation(lxor,(variable(b),(variable(c),())))).
bool_evaluate(variable(c)).
bool_evaluate(variable(b),dummy).
ensure(variable(c),dammy).

x(B) :- bool_evaluated(operation(lxor,(variable(b),(variable(c),()))),val(bool,B)).
b(B) :- bool_evaluated(variable(b),val(bool,B)).
c(B) :- bool_evaluated(variable(c),val(bool,B)).

works :- #count { x : x(true); b : b(true) } = 1.
