% Regression: variadic integer addition over many multi-valued variables.
% Should avoid grounding Cartesian products for variadic add.

#const domain_max = 3.
#const target_sum = 21.

variable_declare(x1, fromFacts, d_x1).
variable_domain(x1, val(int, 1..domain_max)).

variable_declare(x2, fromFacts, d_x2).
variable_domain(x2, val(int, 1..domain_max)).

variable_declare(x3, fromFacts, d_x3).
variable_domain(x3, val(int, 1..domain_max)).

variable_declare(x4, fromFacts, d_x4).
variable_domain(x4, val(int, 1..domain_max)).

variable_declare(x5, fromFacts, d_x5).
variable_domain(x5, val(int, 1..domain_max)).

variable_declare(x6, fromFacts, d_x6).
variable_domain(x6, val(int, 1..domain_max)).

variable_declare(x7, fromFacts, d_x7).
variable_domain(x7, val(int, 1..domain_max)).

variable_declare(x8, fromFacts, d_x8).
variable_domain(x8, val(int, 1..domain_max)).

variable_declare(x9, fromFacts, d_x9).
variable_domain(x9, val(int, 1..domain_max)).

variable_declare(x10, fromFacts, d_x10).
variable_domain(x10, val(int, 1..domain_max)).

variable_define(
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
    ),
    d_sum
).

ensure(operation(eq, (variable(sum), (val(int, target_sum), ()))), sum_matches_target).
