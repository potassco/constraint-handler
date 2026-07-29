% Variant: frontwheel default condition is expression-based.
default_mode(define).

variable_define(backwheel,val(int,20)).
variable_default(frontwheel,variable(backwheel),val(bool,true)).
