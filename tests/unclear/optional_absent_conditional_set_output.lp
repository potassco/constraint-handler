% Regression for compile2 going unsat when an optional set-valued variable is
% controlled by a derived presence flag and a conditional set-valued output is
% absent in the same branch.

ensure((exists_rule,opt),operation(limp,(operation(conj,(operation(lnot,(operation(eq,(variable(opt),(variable(cond),()))),())),())),(val(bool,false),())))).
ensure((link_out_has,(out,child)),operation(limp,(operation(hasValue,(variable(out),())),(variable(opt),())))).
ensure((child_has,(child,opt)),operation(eq,(operation(hasValue,(variable(child),())),(variable(opt),())))).
ensure((inactive_set,child),operation(limp,(operation(lnot,(variable(opt),())),(operation(eq,(variable(s0(child)),(operation(set_make,()),()))),())))).

variable_define(i,i,val(int,2)).
variable_define(cond,cond,operation(neq,(variable(i),(val(int,2),())))).
variable_declare(opt,opt,boolDomain).
variable_define(child,child,operation(if,(variable(opt),(variable(s0(child)),())))).
variable_define(out,out,variable(loc_out)).
variable_define(loc_out,loc_out,operation(ite,(operation(eq,(variable(i),(val(int,1),()))),(variable(loc_t),(val(none,none),()))))).
variable_define(loc_t,loc_t,operation(set_make,())).

set_baseDomain(child,s0(child),val(string,"A")).
set_declare(child,s0(child)).
