variable_declare(s,set).
variable_define(enabled,val(bool,true)).
set_assign(s,val(int,1)).
set_assign(s,val(int,2),val(bool,false)).
set_assign(s,val(int,3),val(bool,true)).
set_assign(s,val(int,4),val(bool,true),named).
set_assign(s,val(int,5),variable(enabled)).

variable_declare(include,fromFacts).
variable_domain(include,val(bool,(false;true))).
variable_declare(candidates,set).
set_baseDomain(candidates,val(int,6)).
set_assign(candidates,val(int,6),variable(include)).
