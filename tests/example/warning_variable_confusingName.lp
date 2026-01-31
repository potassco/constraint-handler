%%% raise the respective warning(variable(confusingName),(),((),_))
variable_define(d_c1,variable(x),val(bool,true)).
variable_define(d_c2,variable,val(bool,true)).
variable_define(d_c3,int,val(bool,true)).
variable_define(d_c4,float,val(bool,true)).
variable_define(d_c5,bool,val(bool,true)).
variable_define(d_c6,none,val(bool,true)).
variable_define(d_c7,str,val(bool,true)).
variable_define(d_c8,symbol,val(bool,true)).
variable_define(d_c9,set,val(bool,true)).
variable_define(d_c10,multimap,val(bool,true)).
variable_define(d_c11,set(int),val(bool,true)).
variable_define(d_c12,set(12),val(bool,true)).
variable_define(d_c13,13,val(bool,true)).
variable_define(d_c14,add,val(bool,true)).

%%% raise no warning
variable_define(d_c15,x,val(bool,true)).
variable_define(d_c16,x(16),val(bool,true)).
variable_define(d_c17,x(set),val(bool,true)).
variable_define(d_c18,x(variable),val(bool,true)).
variable_define(d_c19,"float",val(bool,true)).
