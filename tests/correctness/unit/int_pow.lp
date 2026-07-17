variable_declare(i_neg,fromFacts).
variable_domain(i_neg,val(int,-3)).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(i_three,fromFacts).
variable_domain(i_three,val(int,3)).

variable_declare(i_zero,fromFacts).
variable_domain(i_zero,val(int,0)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(pow,(variable(i_two),(variable(i_three),()))).
evaluate(pow,(variable(i_neg),(variable(i_two),()))).
evaluate(pow,(variable(none_case),(variable(i_zero),()))).
evaluate(pow,(variable(bad_case),(variable(i_zero),()))).
evaluate(pow,(variable(i_two),(variable(none_case),()))).
evaluate(pow,(variable(i_two),(variable(bad_case),()))).
evaluate(pow,(variable(bad_case),(variable(i_three),()))).

#show evaluated/3.
