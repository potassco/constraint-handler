% Regression for compile2 losing set membership when a set-valued variable is
% defined through if/ite and constrained to equal an empty linked output.

ensure((child_has,(child,opt)),operation(eq,(operation(hasValue,(variable(child),())),(variable(opt),())))).
ensure((out_eq_child,(out,child)),operation(eq,(variable(out),(variable(child),())))).
ensure((active_empty,(child,opt)),operation(limp,(variable(opt),(operation(eq,(variable(child),(operation(set_make,()),()))),())))).

variable_define(i,i,val(int,1)).
variable_define(opt,opt,operation(neq,(variable(i),(val(int,2),())))).
variable_define(child,child,operation(if,(variable(opt),(variable(s0(child)),())))).
variable_define(out,out,variable(loc_out)).
variable_define(loc_out,loc_out,operation(ite,(operation(eq,(variable(i),(val(int,1),()))),(variable(loc_t),(val(none,none),()))))).
variable_define(loc_t,loc_t,operation(set_make,())).

set_baseDomain(child,s0(child),val(string,"A")).
set_declare(child,s0(child)).

#show value/2.
#show set_value/2.
