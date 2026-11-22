variable_declare(integer,fromFacts).
variable_domain(integer,val(int,42)).
variable_domain(integer,val(int,43)).
variable_declare(boolean,boolDomain).
variable_declare(forced_condition,boolDomain).
ensure(variable(forced_condition)).
variable_declare(defined,definition,variable(forced_condition)).
variable_define(defined,val(int,7)).
variable_declare(conditional,definition,variable(boolean)).
variable_define(conditional,val(int,8)).
variable_declare(failed,definition).
variable_define(failed,bad).
variable_declare(empty_set,set).
variable_declare(defined_set,set).
set_assign(defined_set,val(int,1)).
variable_declare(inactive,definition,val(bool,false)).
variable_define(inactive,val(int,7)).
not_defined(X) :- variable_declare(X,D), not variable_defined(X).
not_defined(X) :- variable_declare(X,D,C), not variable_defined(X).
