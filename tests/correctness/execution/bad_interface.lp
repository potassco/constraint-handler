execution_declare(prg,STMT,(x,()),(y,())) :-
  STMT = if(variable(x),
            assign(y,val(int,3)),
            assign(y,operation(int_div,(val(int,3),(val(int,0),()))))).

execution_run(prg).

variable_declare(execution_input(prg,x),boolDomain).
ensure(variable(execution_input(prg,x))).

variable_define(z,operation(add,(val(int,2),(variable(execution_output(prg,y)),())))).


variable_define(t,operation(int_div,(val(int,4),(val(int,0),())))).
