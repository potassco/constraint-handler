% Regression: variadic integer addition over many multi-valued variables.
% Should avoid grounding Cartesian products for variadic add.

#const x_count = 10.
#const domain_max = 3.

variable_declare(x(1..x_count),fromFacts).
variable_domain(x(1..x_count),val(int,1..domain_max)).

sum_arguments(x_count,()).
sum_arguments(I,(variable(x(I+1)),Rest)) :-
    I >= 0,
    sum_arguments(I + 1,Rest).

variable_define(
    sum,
    operation(add,Arguments),
    val(bool,true),
    d_sum
) :- sum_arguments(0,Arguments).

ensure(operation(eq,(variable(sum),(val(int,x_count * (domain_max + 1) / 2 + 1),()))),sum_matches_target).
