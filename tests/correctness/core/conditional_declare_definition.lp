variable_declare(enabled,boolDomain).

variable_declare(disabled,definition,val(bool,false)).
variable_define(disabled,val(int,1)).

variable_declare(active,definition,val(bool,true)).
variable_define(active,val(int,2)).

variable_declare(dynamic,definition,variable(enabled)).
variable_define(dynamic,val(int,3)).

variable_declare(always,definition,variable(enabled),when_enabled).
variable_declare(always,definition,operation(lnot,(variable(enabled),())),when_disabled).
variable_define(always,val(int,4)).