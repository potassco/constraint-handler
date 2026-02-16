% Here, a test 
% - passes: if a variable is typed when it should be 
% - fails:  if a variable is typed when it should not be

typed(VAR) :- type_variable(_, VAR, _).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPECTED TO PASS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Variables
variable_declare(check, v(int), fromFacts).
variable_domain(v(int), val(int,3)).
variable_declare(check, v(float), fromFacts).
variable_domain(v(float), val(float,float("3.14"))).
variable_declare(check, v(str), fromFacts).
variable_domain(v(str), val(str, "some_string")).
variable_declare(check, v(bool), boolDomain).
variable_declare(check, v(symbol), fromFacts).
variable_domain(v(symbol), val(symbol, some_symbol)).
variable_define(check, v(none), val(none,none)).

% Addition / multiplication for 0 to N (here 5) numeric types
numeric_args(0, ()).
numeric_args(N, (HEAD,TAIL)) :- 
    HEAD = variable(v(T)), 
    numeric_args(N-1, TAIL), 
    T = (int;float), 
    N=1..5.

variable_define(check, check(OP, N, numeric), EXPR) :- 
    EXPR = operation(OP, ARGS),
    OP = (add;mult),
    numeric_args(N, ARGS).

% Implication for none / bool
variable_define(check, check(OP, 2, none_bool), EXPR) :- 
    EXPR = operation(OP, (variable(v(T1)),(variable(v(T2)),()))),
    OP = limp,
    T1 = (none;bool), 
    T2 = (none;bool).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPECTED TO FAIL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Addition / multiplication with non-numeric types
variable_define(check, check(OP, 2, non_numeric), EXPR) :- 
    EXPR = operation(OP, (variable(v(T1)),(variable(v(T2)),()))),
    OP = (add;mult), 
    T1 = (str;bool), 
    T2 = (str;bool).

% Implication for non none / bool
variable_define(check, check(OP, 2, non_none_bool), EXPR) :- 
    EXPR = operation(OP, (variable(v(T1)),(variable(v(T2)),()))),
    OP = limp,
    T1 = (str;int), 
    T2 = (str;int).
