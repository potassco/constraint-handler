%%% doesn't raise anything
variable_declare(execution_input(itsfine,x),boolDomain).
variable_define(execution_input(itsfine,y),val(int,3)).
variable_declare(d_z,execution_input(itsfine,z),boolDomain).
variable_define((istfine,a),val(int,3)).
variable_define(a,val(int,3)).
execution_declare(itsfine,assign(a,val(int,2)),(x,(y,(z,()))),(a,())).

%%% raise warning(variable(reservedName),...)
execution_declare(itsbad,assign(a,val(int,2)),(x,(y,(z,()))),(a,())).

variable_declare(execution_output(itsbad,x),boolDomain).
variable_define(execution_output(itsbad,y),val(int,3)).
variable_declare(d_z,execution_output(itsbad,z),boolDomain).
set_declare(execution_output(itsbad,t)).
multimap_declare(execution_output(itsbad,u)).
variable_define(execution_output(itsbad,a),val(int,1)).
variable_define(execution_output(itsbad,b),val(int,1)).

%%% raise warning(variable(reservedName),...)
execution_declare(alsobad,assign(a,val(int,2)),(x,(y,(z,()))),(a,())).
execution_run(alsobad).

variable_declare(execution_output(alsobad,x),boolDomain).
variable_define(execution_output(alsobad,y),val(int,3)).
variable_declare(d_z,execution_output(alsobad,z),boolDomain).
variable_declare(execution_output(alsobad,t),set).
variable_declare(execution_output(alsobad,u),multimap).
variable_define(execution_output(alsobad,a),val(int,1)).
variable_define(execution_output(alsobad,b),val(int,1)).

%%% raise warning(variable(reservedName),...)
variable_define(execution_output(notanybetter,x),val(bool,true)).
variable_define(loc(insideIsReserved),val(bool,true)).

#show warning/3.
#show value/2.
