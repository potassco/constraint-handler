variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).
variable_define(subtwoten,operation(sub,(variable(two),(variable(ten),())))).
variable_define(subtentwo,operation(sub,(variable(ten),(variable(two),())))).

evaluate(abs,(variable(subtwoten),())).
evaluate(abs,(variable(subtentwo),())).
