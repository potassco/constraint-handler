% Variant: single default on frontwheel that is coupled to backwheel via ensure.
default_mode(depends).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).

variable_define(backwheel,val(int,20)).
