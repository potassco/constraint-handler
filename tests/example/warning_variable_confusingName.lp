%%% raise the respective warning(variable(confusingName),(),((),_))
variable_define(variable(x),val(bool,true)).
variable_define(variable,val(bool,true)).
variable_define(int,val(bool,true)).
variable_define(float,val(bool,true)).
variable_define(bool,val(bool,true)).
variable_define(none,val(bool,true)).
variable_define(str,val(bool,true)).
variable_define(symbol,val(bool,true)).
variable_define(set,val(bool,true)).
variable_define(multimap,val(bool,true)).
variable_define(set(int),val(bool,true)).
variable_define(set(12),val(bool,true)).
variable_define(13,val(bool,true)).
variable_define(add,val(bool,true)).

%%% raise no warning
variable_define(x,val(bool,true)).
variable_define(x(16),val(bool,true)).
variable_define(x(set),val(bool,true)).
variable_define(x(variable),val(bool,true)).
variable_define("float",val(bool,true)).
