% Variant: default value for backwheel matches its explicit definition.
default_mode(depends).

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true)).
variable_default(backwheel,val(int,20),val(bool,true)).

variable_define(backwheel,val(int,20)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).
