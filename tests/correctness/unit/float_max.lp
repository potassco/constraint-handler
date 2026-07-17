variable_declare(f_small,fromFacts).
variable_domain(f_small,val(float,float("1.5"))).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(max,(variable(f_small),(variable(i_two),()))).
evaluate(max,(variable(f_small),(variable(none_case),()))).
evaluate(max,(variable(f_small),(variable(bad_case),()))).

#show evaluated/3.
