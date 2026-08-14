% Variant: frontwheel default condition is expression-based.
default_mode(depends).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

variable_assign(backwheel,val(int,20)).
variable_default(frontwheel,variable(backwheel),val(bool,true)).
