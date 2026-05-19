variable_define(execution_input(prg,x),val(int,1)).
execution_declare(prg,if(operation(neq,(variable(x),(val(int,1),()))),assert(val(bool,false)),noop),(x,()),()).
execution_run(prg).