phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,4)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(python("bool"),(variable(x),())).


variable_define(pool,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(python("abs"),(val(int,-3),())).
evaluate(python("pow"),(val(int,2),(val(int,5),()))).
evaluate(python("bool"),(val(int,4),())).
evaluate(python("bool"),(val(none,none),())).
evaluate(python("bool"),(bad,())).
evaluate(python("set.__contains__"),(variable(pool),(val(int,2),()))).
