% Cautious output: c = True, m, 1 in s2
% Brave output: a = 1, a = 2, b = 1, b = 2, c = True, m, p, q, 1 in s1, 2 in s1, 1 in s2, 2 in s2
% (does not show the different possible sets or multimaps)


1{p;q}1.
m :- p.
m :- q.


variable_declare(a,fromFacts).
variable_domain(a,val(int,(1..2))).
variable_declare(b,fromFacts).
variable_domain(b,val(int,(1..2))).

variable_declare(c,boolDomain).

ensure(operation(eq,(variable(c),(val(bool,true),())))).

set_declare(s1).
{set_assign(s1,val(int,1..2))}.

set_declare(s2).
set_assign(s2,val(int,1)).
{set_assign(s2,val(int,2))}.
{set_assign(s2,variable(a))}.


multimap_declare(m1).
{multimap_assign(m1,val(int,1),val(int,1))}.
{multimap_assign(m1,val(int,1),val(int,2))}.
multimap_assign(m1,val(int,2),val(int,1)).
