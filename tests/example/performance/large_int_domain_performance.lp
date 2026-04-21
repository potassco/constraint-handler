% Compile benchmark: large integer domain with a unique satisfying boundary value.

#const int_domain_size = 10000.

variable_declare(assign_x, x, fromFacts).
variable_domain(x, val(int, 1..int_domain_size)).

variable_define(assign_y, y, operation(add, (variable(x), (val(int, 1), ())))).

ensure(max_domain_value, operation(eq, (variable(y), (val(int, int_domain_size + 1), ())))).
