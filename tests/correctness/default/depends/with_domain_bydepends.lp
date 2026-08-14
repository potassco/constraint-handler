% Variant: default value for backwheel matches its explicit definition.
default_mode(depends).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

variable_default(frontwheel,val(int,20)).
variable_default(frontwheel,val(int,21)).
variable_default(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true),1).
variable_default(backwheel,val(int,21),val(bool,true),1).

variable_assign(backwheel,val(int,20)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).
