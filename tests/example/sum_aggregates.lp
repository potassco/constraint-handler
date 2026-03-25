% Regression: variadic integer addition over many multi-valued variables
% Should avoid grounding Cartesian products for variadic add.
%
% 10 integer variables with domain 1..3

variable_declare(d_x1,  x1,  fromFacts).
variable_domain(x1,  val(int, 1..3)).

variable_declare(d_x2,  x2,  fromFacts).
variable_domain(x2,  val(int, 1..3)).

variable_declare(d_x3,  x3,  fromFacts).
variable_domain(x3,  val(int, 1..3)).

variable_declare(d_x4,  x4,  fromFacts).
variable_domain(x4,  val(int, 1..3)).

variable_declare(d_x5,  x5,  fromFacts).
variable_domain(x5,  val(int, 1..3)).

variable_declare(d_x6,  x6,  fromFacts).
variable_domain(x6,  val(int, 1..3)).

variable_declare(d_x7,  x7,  fromFacts).
variable_domain(x7,  val(int, 1..3)).

variable_declare(d_x8,  x8,  fromFacts).
variable_domain(x8,  val(int, 1..3)).

variable_declare(d_x9,  x9,  fromFacts).
variable_domain(x9,  val(int, 1..3)).

variable_declare(d_x10, x10, fromFacts).
variable_domain(x10, val(int, 1..3)).

% Define a helper variable "sum" as x1 + ... + x10
variable_define(d_sum, sum,
    operation(add, (variable(x1),
        (variable(x2),
        (variable(x3),
        (variable(x4),
        (variable(x5),
        (variable(x6),
        (variable(x7),
        (variable(x8),
        (variable(x9),
        (variable(x10), ())))))))))))).

% Ensure sum == 27
ensure(sum_is_27, operation(eq, (variable(sum), (val(int, 27), ())))).
