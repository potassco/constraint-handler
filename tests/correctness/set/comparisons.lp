variable_declare(declared_set,set).
set_assign(declared_set,val(int,(1;2;3))).

variable_define(made_set_1,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(made_set_2,operation(set_make,(val(int,1),(val(int,2),())))).

evaluate(operation(eq,(variable(declared_set),(variable(made_set_1),())))).
evaluate(operation(neq,(variable(declared_set),(variable(made_set_2),())))).

evaluate(operation(eq,(variable(declared_set),(val(none,none),())))).
evaluate(operation(neq,(val(none,none),(variable(declared_set),())))).

evaluate(operation(eq,(variable(declared_set),(val(int,1),())))).
evaluate(operation(neq,(val(int,1),(variable(declared_set),())))).
