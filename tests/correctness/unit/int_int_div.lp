variable_declare(i_four,fromFacts).
variable_domain(i_four,val(int,4)).

variable_declare(i_neg,fromFacts).
variable_domain(i_neg,val(int,-4)).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(i_zero,fromFacts).
variable_domain(i_zero,val(int,0)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(int_div,(variable(i_four),(variable(i_two),()))).
evaluate(int_div,(variable(i_neg),(variable(i_two),()))).
evaluate(int_div,(variable(i_four),(variable(i_zero),()))).
evaluate(int_div,(variable(i_four),(variable(none_case),()))).
evaluate(int_div,(variable(i_four),(variable(bad_case),()))).

#show evaluated/3.
