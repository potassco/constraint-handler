variable_declare(enabled,boolDomain).
variable_declare(items,set,variable(enabled),when_enabled).
variable_declare(items,set,operation(lnot,(variable(enabled),())),when_disabled).
set_assign(items,val(int,1)).