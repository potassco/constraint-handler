variable_declare(int_case,fromFacts).
variable_domain(int_case,val(int,4)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

variable_define(pool,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(python("2"),()).
evaluate(python("abs"),(val(int,-3),())).
evaluate(python("pow"),(val(int,2),(val(int,5),()))).
evaluate(python("bool"),(variable(int_case),())).
evaluate(python("bool"),(variable(none_case),())).
evaluate(python("bool"),(variable(bad_case),())).
evaluate(python("set.__contains__"),(variable(pool),(val(int,2),()))).

#show evaluated/3.
