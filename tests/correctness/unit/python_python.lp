variable_declare(x,fromFacts).
variable_domain(x,val(int,4)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(python("bool"),(variable(x),()))).


variable_define(pool,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(operation(python("abs"),(val(int,-3),()))).
evaluate(operation(python("pow"),(val(int,2),(val(int,5),())))).
evaluate(operation(python("bool"),(val(int,4),()))).
evaluate(operation(python("bool"),(val(none,none),()))).
evaluate(operation(python("bool"),(bad,()))).
evaluate(operation(python("set.__contains__"),(variable(pool),(val(int,2),())))).
