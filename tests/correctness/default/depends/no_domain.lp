% Variant: frontwheel default condition is expression-based.
default_mode(depends).

variable_define(backwheel,val(int,20)).
variable_default(frontwheel,variable(backwheel),val(bool,true)).
