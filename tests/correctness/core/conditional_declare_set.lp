variable_declare(enabled,boolDomain).
variable_declare(active_set,set,val(bool,true)).
variable_declare(disabled_set,set,val(bool,false)).
variable_declare(dynamic_set,set,variable(enabled)).
set_assign(active_set,val(int,1)).
set_assign(disabled_set,val(int,1)).
set_assign(dynamic_set,val(int,1)).
