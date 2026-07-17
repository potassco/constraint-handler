variable_declare(f_large,fromFacts).
variable_domain(f_large,val(float,float("2.5"))).

variable_declare(f_zero,fromFacts).
variable_domain(f_zero,val(float,float("0.0"))).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(mult,()).
evaluate(mult,(variable(f_large),())).
evaluate(mult,(variable(f_large),(variable(i_two),()))).
evaluate(mult,(variable(f_zero),(variable(bad_case),()))).
evaluate(mult,(variable(f_large),(variable(none_case),()))).
evaluate(mult,(variable(f_large),(variable(bad_case),()))).

#show evaluated/3.
