% Variant: frontwheel default is disabled by a definition.
default_mode(depends).

% This should be allowed to be here!
%variable_domain(frontwheel,val(int,20)).
%variable_domain(frontwheel,val(int,21)).
%variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true)).

variable_define(frontwheel,val(int,20)).

#show -_default_apply/3.