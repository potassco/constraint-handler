#include "includeAll.lp".
% Cautious output: c = True
% Brave output: a = 1, a = 2, b = 1, b = 2, c = True

variable_declare(dummy,a,fromFacts).
variable_domain(a,val(int,(1..2))).
variable_declare(dummy,b,fromFacts).
variable_domain(b,val(int,(1..2))).

variable_declare(dummy,c,boolDomain).

ensure(dummy,operation(eq,(variable(c),(val(bool,true),())))).
