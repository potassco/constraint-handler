variable_declare(i_neg,fromFacts).
variable_domain(i_neg,val(int,-3)).

variable_declare(i_two,fromFacts).
variable_domain(i_two,val(int,2)).

variable_declare(b_true,fromFacts).
variable_domain(b_true,val(bool,true)).

variable_declare(b_false,fromFacts).
variable_domain(b_false,val(bool,false)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(add,()).
evaluate(add,(variable(i_neg),())).
evaluate(add,(variable(b_true),())).
evaluate(add,(variable(i_two),(variable(b_true),()))).
evaluate(add,(variable(i_two),(variable(b_false),()))).
evaluate(add,(variable(i_neg),(variable(i_two),(variable(b_true),())))).
evaluate(add,(variable(i_two),(variable(none_case),()))).
evaluate(add,(variable(i_two),(variable(bad_case),()))).

#show evaluated/3.
