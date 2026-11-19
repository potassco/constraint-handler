variable_define(enabled,val(bool,true)).
variable_declare(active,definition,val(bool,true)).
variable_declare(inactive,definition,val(bool,false)).
variable_declare(bad_condition,definition,bad).
variable_declare(conditional,definition,variable(enabled)).
variable_declare(multiple,definition,val(bool,false)).
variable_declare(multiple,definition,val(bool,true)).
variable_declare(empty_set,set).
