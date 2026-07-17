variable_declare(f_small,fromFacts).
variable_domain(f_small,val(float,float("1.5"))).

variable_declare(f_large,fromFacts).
variable_domain(f_large,val(float,float("2.5"))).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(neq,(variable(f_large),(val(float,float("2.5")),()))).
evaluate(neq,(variable(i_two),(val(float,float("2.0")),()))).
evaluate(neq,(variable(none_case),(variable(none_case),()))).
evaluate(neq,(variable(f_small),(variable(none_case),()))).
evaluate(neq,(variable(f_small),(variable(bad_case),()))).

#show evaluated/3.
