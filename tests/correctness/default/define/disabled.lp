% Variant: frontwheel default is disabled by a false condition.
default_mode(define).

variable_declare(frontwheel,open).

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,false),2).
