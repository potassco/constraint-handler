variable_declare(integer,fromFacts).
variable_domain(integer,val(int,(1;2))).
variable_declare(boolean,boolDomain).
variable_declare(conditional,definition,variable(boolean)).
variable_define(conditional,val(int,7)).
variable_declare(floating,definition).
variable_define(floating,val(float,float("1.5"))).
variable_declare(string,definition).
variable_define(string,val(string,"text")).
variable_declare(none,definition).
variable_define(none,val(none,none)).
variable_declare(empty_set,set).
variable_declare(defined_set,set).
set_assign(defined_set,val(int,1)).
variable_declare(failed,definition).
variable_define(failed,bad).
variable_declare(inactive,definition,val(bool,false)).
variable_define(inactive,val(int,7)).
variable_declare(dynamic,fromFacts).
variable_domain(dynamic,(val(int,3);val(string,"three"))).
typed_as(X,T) :- variable_typed(X,T).
not_typed(X) :- variable_declare(X,D), not variable_typed(X,_).
not_typed(X) :- variable_declare(X,D,C), not variable_typed(X,_).