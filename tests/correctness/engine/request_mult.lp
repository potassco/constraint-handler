%%% atomic -> set
variable_define(as_a,val(int,3),assign_as_a).
variable_declare(as_s,set,assign_as_s).
set_assign(as_s,val(int,2),assign_as_s).
set_assign(as_s,variable(as_a),assign_as_s).

engine_request(assign_as_a, compile).
engine_request(assign_as_s, ground).


%%% (set,set) -> set
variable_declare(sss_s1,set,assign_sss_s1).
set_assign(sss_s1,val(int,1),assign_sss_s1).
set_assign(sss_s1,val(int,2),assign_sss_s1).
variable_declare(sss_s2,set,assign_sss_s2).
set_assign(sss_s2,val(int,2),assign_sss_s2).
set_assign(sss_s2,val(int,3),assign_sss_s2).
variable_define(sss_s3,operation(inter,(variable(sss_s1),(variable(sss_s2),()))),assign_sss_s3).

engine_request(assign_sss_s1,compile).
engine_request(assign_sss_s2,ground).
engine_request(assign_sss_s3,compile).


%%% set -> atomic


%%% (set,set) -> atomic
%%% ssa_s1 = {1,2}
%%% ssa_s2 = {1,2,3}
%%% ssa_a = ssa_s1 \subseteq ssa_s2
variable_declare(ssa_s1,set,assign_ssa_s1).
set_assign(ssa_s1,val(int,1),assign_ssa_s1).
set_assign(ssa_s1,val(int,2),assign_ssa_s1).
variable_declare(ssa_s2,set,assign_ssa_s2).
set_assign(ssa_s2,val(int,2),assign_ssa_s2).
set_assign(ssa_s2,val(int,3),assign_ssa_s2).
variable_define(ssa_a,operation(subset,(variable(ssa_s1),(variable(ssa_s2),()))),assign_ssa_a).

engine_request(assign_ssa_s1,compile).
engine_request(assign_ssa_s2,ground).
engine_request(assign_ssa_a,propagator).

warning_ignore(type(failed_operation)).
