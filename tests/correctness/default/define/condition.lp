% Variant: frontwheel default condition is expression-based.
% The default for frontwheel is active only when backwheel == 1.
default_mode(define).

variable_domain(frontwheel,val(int,10)).
variable_domain(frontwheel,val(int,20)).
variable_domain(frontwheel,val(int,30)).

variable_default(frontwheel,val(int,20),operation(eq,(variable(backwheel),(val(int,1),())))).

evaluate(add,(variable(frontwheel),(variable(backwheel),()))).

1 { variable_define(backwheel,val(int,(1;2))) } 1.
