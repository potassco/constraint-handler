% Variant: frontwheel default is disabled by a definition.
default_mode(depends).

variable_declare(frontwheel,open).

% This should be allowed to be here!
variable_default(frontwheel,val(int,20)).
variable_default(frontwheel,val(int,21)).
variable_default(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true),2).

variable_assign(frontwheel,val(int,20)).
