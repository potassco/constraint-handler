% Here, a test
% - passes: if a variable is typed when it should be
% - fails:  if a variable is typed when it should not be

typed(VAR) :- type_variable(_, VAR, _).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPECTED TO PASS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Static variable declarations
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
1{arity(N):N=1..5}1.
count(1..N) :- arity(N).

numeric_args(0, (int;non_int),()).
numeric_args(N, int, (variable(v(int)), TAIL)) :- numeric_args(N-1, int, TAIL), count(N).

1{numeric_args(N, non_int, (variable(v(T)),TAIL)):T = (int;float)}1 :-
    numeric_args(N-1, non_int, TAIL),
    count(N),
    arity(A),
    N < A.

numeric_args(N, non_int, (variable(v(float)), TAIL)) :- numeric_args(N-1, non_int, TAIL), arity(N).

variable_define(check, check(OP, numeric(TYPES)), EXPR) :-
    EXPR = operation(OP, ARGS),
    OP = (add;mult),
    numeric_args(N, TYPES, ARGS),
    arity(N).

1 {none_bool(N,T):T = (none;bool)} 1 :- N=1..2.

% Implication for none / bool
variable_define(check, check(OP, none_bool), EXPR) :-
    EXPR = operation(OP, (variable(v(T1)),(variable(v(T2)),()))),
    OP = limp,
    none_bool(1, T1),
    none_bool(2, T2).

% Multimap make
variable_define(check, check(multimap_make_empty), operation(multimap_make, ())).
variable_define(check, check(multimap_make), MAP) :-
    MAP = operation(multimap_make, (ITEM1,(ITEM2,(ITEM3,())))),
    KEY = variable(v(str)),
    ITEM1 = (KEY, variable(v(int))),
    ITEM2 = (KEY, variable(v(float))),
    KEY2 = variable(v(symbol)),
    ITEM3 = (KEY2, variable(v(int))).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EXPECTED TO FAIL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Addition / multiplication with non-numeric types
variable_define(check, check(OP, non_numeric), EXPR) :-
    EXPR = operation(OP, (ARG1,(ARG2,()))),
    OP = (add;mult),
    ARG1 = variable(v(str)),
    ARG2 = variable(v(bool)).

% Implication for non none / bool
variable_define(check, check(OP, non_none_bool), EXPR) :-
    EXPR = operation(OP, (ARG1,(ARG2,()))),
    OP = limp,
    ARG1 = variable(v(str)),
    ARG2 = variable(v(int)).
