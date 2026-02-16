%%% atomic -> set
variable_define(assign_as_a,as_a,val(int,3)).
set_declare(assign_as_s,as_s).
set_assign(assign_as_s,as_s,val(int,2)).
set_assign(assign_as_s,as_s,variable(as_a)).

%requestEngine(assign_as_a, compile).
%requestEngine(assign_as_s, ground).


%%% (set,set) -> set
set_declare(assign_sss_s1,sss_s1).
set_assign(assign_sss_s1,sss_s1,val(int,1)).
set_assign(assign_sss_s1,sss_s1,val(int,2)).
set_declare(assign_sss_s2,sss_s2).
set_assign(assign_sss_s2,sss_s2,val(int,2)).
set_assign(assign_sss_s2,sss_s2,val(int,3)).
variable_define(assign_sss_s3,sss_s3,operation(inter,(variable(sss_s1),(variable(sss_s2),())))).

%requestEngine(assign_sss_s1, compile).
%requestEngine(assign_sss_s2, ground).
%requestEngine(assign_sss_s3, compile).


%%% set -> atomic


%%% (set,set) -> atomic
%%% ssa_s1 = {1,2}
%%% ssa_s2 = {1,2,3}
%%% ssa_a = ssa_s1 \subseteq ssa_s2
set_declare(assign_ssa_s1,ssa_s1).
set_assign(assign_ssa_s1,ssa_s1,val(int,1)).
set_assign(assign_ssa_s1,ssa_s1,val(int,2)).
set_declare(assign_ssa_s2,ssa_s2).
set_assign(assign_ssa_s2,ssa_s2,val(int,2)).
set_assign(assign_ssa_s2,ssa_s2,val(int,3)).
variable_define(assign_ssa_a,ssa_a,operation(subset,(variable(ssa_s1),(variable(ssa_s2),())))).

%requestEngine(assign_ssa_s1, compile).
%requestEngine(assign_ssa_s2, ground).
%requestEngine(assign_ssa_a, propagator).

#show value/2.
#show set_value/2.
#show warning/3.

ignore_warning(type(failed_operation)).