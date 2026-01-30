%%%%%%%%%%%%%%%%% Setup
% All types
test_type(int; float; str; bool; symbol; none; set; multimap).

% Variables
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

% Special case: Some operators don't work with all values!
restricted_domain(acos; asin).

variable_declare(check, v(safe_float), fromFacts).
variable_domain(v(safe_float), val(float, float("0.5"))).


% Shortcut for warnings
test_operation_warning(OP, TS) :- warning(type(failed_operation),(),((),OP,(variable(v(T)),()))), TS = (T,()).
test_operation_warning(OP, TS) :- warning(type(failed_operation),(),((),OP,(variable(v(T1)),(variable(v(T2)),())))), TS = (T1,(T2,())).

%%%%%%%%%%%%%%%%%%
% There's currently at keast one problem with this approach: The Python side doesn't seem to do type checking, 
% which results in error messages in a manual run and crashes in a test run.
%%%%%%%%%%%%%%%%%%

% Transform into unary, binary and variadic operators
% test_unaryOperator(OP) :- numericUnFOperator(OP).
% test_unaryOperator(OP) :- numericUnOperator(OP).
% test_unaryOperator(OP) :- OP = (lnot;wnot;snot;countKeys;countEntries;sumIntEntries;length).
test_unaryOperator(OP) :- OP = hasValue.

% test_binaryOperator(OP) :- numericBinOperator(OP).
% test_binaryOperator(OP) :- comparisonOperator(OP).
% test_binaryOperator(OP) :- equalityOperator(OP).
% test_binaryOperator(OP) :- logicOperator(OP).
% test_binaryOperator(OP) :- setOperator(OP).
% test_binaryOperator(OP) :- membershipOperator(OP).
% test_binaryOperator(OP) :- OP = (maxEntries; minEntries; inter).

% test_variadicOperator(add; mult;union).
% test_variadicOperator(OP) :- logicOperator(OP), OP != limp.


variable_define(check, (OP, (T,())), operation(OP, (variable(v(T)),()))) :- 
    test_type(T), 
    test_unaryOperator(OP),
    not restricted_domain(OP).

variable_define(check, (OP, (safe_float,())), operation(OP, (variable(v(safe_float)),()))) :- 
    test_unaryOperator(OP),
    restricted_domain(OP).

% Every combination represents a test case
test_case(OP, TS) :- variable_define(check, (OP, TS), _).

% Conflicts between implementation and type check
test_conflict(OP, TS) :- test_case(OP,TS), not value((OP, TS), _), not test_operation_warning(OP,TS).
test_conflict(OP, TS) :- value((OP, TS), _), test_operation_warning(OP,TS).