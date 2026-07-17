variable_declare(four_case,fromFacts).
variable_domain(four_case,val(int,4)).

variable_declare(two_case,fromFacts).
variable_domain(two_case,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(float_div,(variable(four_case),(variable(two_case),()))).
evaluate(float_div,(variable(four_case),(variable(none_case),()))).
evaluate(float_div,(variable(four_case),(variable(bad_case),()))).

#show evaluated/3.
