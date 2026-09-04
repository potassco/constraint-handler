% Variant: single default on frontwheel that is coupled to backwheel via ensure.
default_mode(define).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

variable_choice(frontwheel,val(int,20)).
variable_choice(frontwheel,val(int,21)).
variable_choice(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true),1).

variable_assign(backwheel,val(int,20)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).
