% Cautious output: c = True, m, 1 in s2
% Brave output: a = 1, a = 2, b = 1, b = 2, c = True, m, p, q, 1 in s1, 2 in s1, 1 in s2, 2 in s2
% (does not show the different possible sets or multimaps)


1{p;q}1.
m :- p.
m :- q.


variable_declare(dummy,a,fromFacts).
variable_domain(a,val(int,(1..2))).
variable_declare(dummy,b,fromFacts).
variable_domain(b,val(int,(1..2))).

variable_declare(dummy,c,boolDomain).

ensure(dummy,operation(eq,(variable(c),(val(bool,true),())))).

set_declare(dummy,s1).
{set_assign(dummy,s1,val(int,1..2))}.

set_declare(dummy,s2).
set_assign(dummy,s2,val(int,1)).
{set_assign(dummy,s2,val(int,2))}.
{set_assign(dummy,s2,variable(a))}.


multimap_declare(dummy,m1).
{multimap_assign(dummy,m1,val(int,1),val(int,1))}.
{multimap_assign(dummy,m1,val(int,1),val(int,2))}.
multimap_assign(dummy,m1,val(int,2),val(int,1)).
