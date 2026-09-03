% Variant: a definition for both wheels recovers satisfiability.
default_mode(define).

variable_declare(frontwheel,open).
variable_declare(backwheel,open).

%This should be allowed to be here!
variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true),1).
variable_default(backwheel,val(int,21),val(bool,true),1).

variable_assign(frontwheel,val(int,20)).
variable_assign(backwheel,val(int,20)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).
