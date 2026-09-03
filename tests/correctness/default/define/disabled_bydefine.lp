% Variant: frontwheel default is disabled by a definition.
default_mode(define).

variable_declare(frontwheel,open).

% This should be allowed to be here!
variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true),1).

variable_assign(frontwheel,val(int,20)).
