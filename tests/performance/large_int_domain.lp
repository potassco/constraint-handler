% Compile benchmark: large integer domain with a unique satisfying boundary value.

#const int_domain_size = 10000.

variable_declare(x, fromFacts, assign_x).
variable_domain(x, val(int, 1..int_domain_size)).

variable_define(y, operation(add, (variable(x), (val(int, 1), ()))), assign_y).

ensure(operation(eq, (variable(y), (val(int, int_domain_size + 1), ()))), max_domain_value).
