% Variant: frontwheel default condition is expression-based.
% The default for frontwheel is active only when backwheel == 21.
% Run with: -c default_mode=define|basic|depends

variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,21)).
variable_domain(frontwheel,val(int,22)).

variable_default(frontwheel,val(int,21),operation(eq,(variable(backwheel),(val(int,21),())))).
variable_default(backwheel,val(int,21),val(bool,true)).

ensure(operation(eq,(variable(frontwheel),(variable(backwheel),())))).

variable_define(backwheel,val(int,20)).

#show _se_value/2.
#show -apply/3.
#show depends/2.
