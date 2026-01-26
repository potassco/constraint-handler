#include "includeAll.lp".
% Cautious output: c = True
% Brave output: a = 1, a = 2, b = 1, b = 2, c = True

variable_declare(dummy,a,fromFacts).
variable_domain(a,val(int,(1..2))).
variable_declare(dummy,b,fromFacts).
variable_domain(b,val(int,(1..2))).

variable_declare(dummy,c,boolDomain).

ensure(dummy,operation(eq,(variable(c),(val(bool,true),())))).

set_declare(dummy,s1).
{set_assign(dummy,s1,val(int,1..2))}.

{stage(1;2)}.
#heuristic stage(1). [99,true]
#heuristic stage(2). [98,true]

#show stage/1.
