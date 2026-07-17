variable_declare(i_three,fromFacts).
variable_domain(i_three,val(int,3)).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(float_div,(variable(i_three),(variable(i_two),()))).
evaluate(float_div,(variable(i_three),(variable(none_case),()))).
evaluate(float_div,(variable(i_three),(variable(bad_case),()))).

#show evaluated/3.
