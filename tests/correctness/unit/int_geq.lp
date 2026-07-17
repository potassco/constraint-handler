variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(i_three,fromFacts).
variable_domain(i_three,val(int,3)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(geq,(variable(i_three),(variable(i_two),()))).
evaluate(geq,(variable(i_two),(variable(i_three),()))).
evaluate(geq,(variable(i_two),(variable(i_two),()))).
evaluate(geq,(variable(i_two),(variable(none_case),()))).
evaluate(geq,(variable(i_two),(variable(bad_case),()))).

#show evaluated/3.
