% Variant: default values for backwheel and frontwheel match.
default_mode(define).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true)).
variable_default(backwheel,val(int,21),val(bool,true)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).
