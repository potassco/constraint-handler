%%% Test set_declare/1 and set_baseDomain/2 where basedomain has multiple expressions assigning the same value
%%%

variable_define(a,val(int,1)).
variable_define(b,val(int,2)).
variable_define(c,val(int,3)).

variable_declare(s,set).
set_baseDomain(s,val(int,1..3)).
set_baseDomain(s,variable(a)).
set_baseDomain(s,variable(b)).
set_baseDomain(s,variable(c)).
