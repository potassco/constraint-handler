% Variant: default value for backwheel matches its explicit definition.
% Run with: -c default_mode=define|basic|depends

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),val(bool,true)).
variable_default(backwheel,val(int,20),val(bool,true)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).

variable_define(backwheel,val(int,20)).

#show _se_value/2.
#show -apply/3.
#show depends/2.
