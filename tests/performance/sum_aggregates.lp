% Regression: variadic integer addition over many multi-valued variables.
% Should avoid grounding Cartesian products for variadic add.

#const domain_max = 3.
#const target_sum = 21.

variable_declare(d_x1, x1, fromFacts).
variable_domain(x1, val(int, 1..domain_max)).

variable_declare(d_x2, x2, fromFacts).
variable_domain(x2, val(int, 1..domain_max)).

variable_declare(d_x3, x3, fromFacts).
variable_domain(x3, val(int, 1..domain_max)).

variable_declare(d_x4, x4, fromFacts).
variable_domain(x4, val(int, 1..domain_max)).

variable_declare(d_x5, x5, fromFacts).
variable_domain(x5, val(int, 1..domain_max)).

variable_declare(d_x6, x6, fromFacts).
variable_domain(x6, val(int, 1..domain_max)).

variable_declare(d_x7, x7, fromFacts).
variable_domain(x7, val(int, 1..domain_max)).

variable_declare(d_x8, x8, fromFacts).
variable_domain(x8, val(int, 1..domain_max)).

variable_declare(d_x9, x9, fromFacts).
variable_domain(x9, val(int, 1..domain_max)).

variable_declare(d_x10, x10, fromFacts).
variable_domain(x10, val(int, 1..domain_max)).

variable_define(
    d_sum,
    sum,
    operation(
        add,
        (
            variable(x1),
            (
                variable(x2),
                (
                    variable(x3),
                    (
                        variable(x4),
                        (
                            variable(x5),
                            (
                                variable(x6),
                                (
                                    variable(x7),
                                    (
                                        variable(x8),
                                        (
                                            variable(x9),
                                            (variable(x10), ())
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
).

ensure(sum_matches_target, operation(eq, (variable(sum), (val(int, target_sum), ())))).
