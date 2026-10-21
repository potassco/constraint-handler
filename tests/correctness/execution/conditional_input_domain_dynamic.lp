execution_declare(prg,assign(y,variable(x)),(x,()),(y,())).

variable_define(enabled,val(bool,false)).
variable_domain(execution_input(prg,x),val(int,1),variable(enabled)).
