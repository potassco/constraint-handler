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
variable_define(check, none_bool((1;2)), fromFacts).
variable_domain(none_bool, val(none,none)).
variable_domain(none_bool, variable(v(bool))).
set_declare(check, v(set)).
set_assign(v(set), variable(v(int))).
multimap_declare(check, v(multimap)).
multimap_assign(v(multimap), variable(v(symbol)), variable(v(int))).

check_types(T) :- variable_declare(_,v(T),_).
check_types(T) :- T = (set;multimap).

%%%%%%%%%%%%%%%%% None
variable_define(check, check(OP, none), EXPR) :-
    EXPR = operation(OP, (variable(v(none)),(variable(v(bool)),()))),
    OP = (eq;neq).

variable_define(check, check(OP, none), EXPR) :-
    EXPR = operation(OP, (variable(v(none)),())),
    OP = (lnot).

%%%%%%%%%%%%%%%%% Bool
variable_define(check, check(OP, bool), EXPR) :-
    EXPR = operation(OP, (variable(v(bool)),())),
    OP = (lnot;snot;wnot).

variable_define(check, check(OP, bool), EXPR) :-
    EXPR = operation(OP, (variable(v(bool)),(variable(v(bool)),()))),
    OP = (eq;neq).

variable_define(check, check(OP, bool), EXPR) :-
    EXPR = operation(OP, (variable(v(bool)),(variable(v(bool)),(variable(v(bool)),())))),
    OP = (conj;disj;lxor;leqv).

variable_define(check, check(OP, none_bool), EXPR) :-
    EXPR = operation(OP, (variable(v(none_bool(1))),(variable(v(none_bool(2))),()))),
    OP = (limp).

%%%%%%%%%%%%%%%%% Int

% Addition / multiplication for 0 to N (here 5) numeric types
1{arity(N):N=1..5}1.
count(1..N) :- arity(N).

_int_args(0,()).
_int_args(N, (variable(v(int)), TAIL)) :- _int_args(N-1, TAIL), count(N).
variable_define(check, check(OP, int), EXPR) :-
    EXPR = operation(OP, ARGS),
    OP = (add;mult),
    _int_args(N, ARGS),
    arity(N).

variable_define(check, check(OP, int), EXPR) :-
    EXPR = operation(OP, (variable(v(int)),(variable(v(int)),()))),
    OP = (sub;div;fdiv;pow;eq;neq;leq;lt;geq;gt).

variable_define(check, check(OP, int), EXPR) :-
    EXPR = operation(OP, (variable(v(int)),())),
    OP = (abs;minus).

%%%%%%%%%%%%%%%%% Float / Mixed

_float_args(0,()).
1{_float_args(N, (variable(v(T)),TAIL)):T = (int;float)}1 :-
    _float_args(N-1, TAIL),
    count(N),
    arity(A),
    N < A.

_float_args(N, (variable(v(float)), TAIL)) :- _float_args(N-1, TAIL), arity(N).

variable_define(check, check(OP, float), EXPR) :-
    EXPR = operation(OP, ARGS),
    OP = (add;mult),
    _float_args(N, ARGS),
    arity(N).

variable_define(check, check(OP, float), EXPR) :-
    EXPR = operation(OP, (variable(v(float)),(variable(v((int;float))),()))),
    OP = (sub;div;fdiv;pow;eq;neq;leq;lt;geq;gt).

variable_define(check, check(OP, float), EXPR) :-
    EXPR = operation(OP, (variable(v(float)),())),
    OP = (abs;minus;floor).

%%%%%%%%%%%%%%%%% str
variable_define(check, check(OP, str), EXPR) :-
    EXPR = operation(OP, (variable(v(str)),(variable(v(str)),()))),
    OP = (eq;neq;concat).

variable_define(check, check(OP, str), EXPR) :-
    EXPR = operation(OP, (variable(v(str)),())),
    OP = length.

%%%%%%%%%%%%%%%%% symbol
variable_define(check, check(OP, symbol), EXPR) :-
    EXPR = operation(OP, (variable(v(symbol)),(variable(v(symbol)),()))),
    OP = (eq;neq;concat).

%%%%%%%%%%%%%%%%% set
variable_define(check, check(OP, set), EXPR) :-
    EXPR = operation(OP, (variable(v(set)),(variable(v(set)),()))),
    OP = (eq;neq;union;inter;diff;subset).

variable_define(check, check(OP, set), EXPR) :-
    EXPR = operation(OP, (variable(v(set)),())),
    OP = length.

variable_define(check, check(OP, set), EXPR) :-
    EXPR = operation(OP, (variable(v(T)),(variable(v(set)),()))),
    check_types(T),
    OP = (isin;notin).

variable_define(check, check(OP), EXPR) :-
    EXPR = operation(OP, (variable(v(int)),(variable(v(int)),(variable(v(int)),())))),
    OP = makeSet.

%%%%%%%%%%%%%%%%% Multimap
variable_define(check, check(OP, multimap), EXPR) :-
    EXPR = operation(OP, (variable(v(multimap)),(variable(v(multimap)),()))),
    OP = (eq;neq).

variable_define(check, check(OP, multimap), EXPR) :-
    EXPR = operation(OP, (variable(v(T)),(variable(v(multimap)),()))),
    check_types(T),
    OP = (isin; find).

variable_define(check, check(OP, multimap), EXPR) :-
    EXPR = operation(OP, (variable(v(multimap)),())),
    OP = (countKeys;countEntries;sumIntEntries;maxEntries;minEntries).

variable_define(check, check(multimap_make_empty), operation(multimap_make, ())).
variable_define(check, check(multimap_make), MAP) :-
    MAP = operation(multimap_make, (ITEM1,(ITEM2,(ITEM3,())))),
    KEY = variable(v(str)),
    ITEM1 = (KEY, variable(v(int))),
    ITEM2 = (KEY, variable(v(float))),
    KEY2 = variable(v(symbol)),
    ITEM3 = (KEY2, variable(v(int))).

%%%%%%%%%%%%%%%%% Conditionals
variable_define(check, check(OP, T), EXPR) :-
    EXPR = operation(OP, (variable(v(T)),())),
    check_types(T),
    OP = (hasValue).

%%%%%%%%%%%%%%%%% More complex
% Chained (multimap_make -> find -> length)
variable_define(check, check(length_find_multimap_make), operation(length, (SET,()))) :-
    SET = operation(find,(KEY,(MAP,()))),
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
