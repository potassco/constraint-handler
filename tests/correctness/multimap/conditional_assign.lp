variable_declare(m,multimap).
variable_define(enabled,val(bool,true)).

multimap_assign(m,val(int,1),val(int,10)).
multimap_assign(m,val(int,2),val(int,20),val(bool,true)).
multimap_assign(m,val(int,3),val(int,30),val(bool,false)).
multimap_assign(m,val(int,4),val(int,40),val(bool,true),active_assignment).
multimap_assign(m,val(int,5),val(int,50),val(bool,false),inactive_assignment).
multimap_assign(m,val(int,6),val(int,60),variable(enabled)).
multimap_assign(m,val(int,7),val(int,70),operation(wnot,(variable(enabled),()))).
multimap_assign(m,val(int,8),val(int,80),bad).

variable_declare(toggle,boolDomain).
variable_declare(dynamic,multimap).
multimap_assign(dynamic,val(int,1),val(int,10),variable(toggle)).
multimap_assign(dynamic,val(int,2),val(int,20),operation(wnot,(variable(toggle),()))).
variable_define(dynamic_count,operation(countEntries,(variable(dynamic),()))).
