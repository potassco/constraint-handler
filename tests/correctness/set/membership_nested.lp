variable_define(v1, operation(add,(val(int,1),(val(int,1),())))).
variable_define(v2, val(int,2)).
variable_define(s1, operation(set_make,
                                   (variable(v1),()))).
variable_define(s2, operation(set_make,
                                   (variable(v2),()))).
variable_define(s3, operation(set_make,
                                   (val(int,3),()))).
variable_define(s4, operation(set_make,
                                   (val(int,4),()))).
variable_define(ss1, operation(set_make,
                                     (variable(s1),(variable(s3),())))).
variable_define(se, operation(union,
                                   (variable(ss1),
                                   (variable(ss1),())))).

%%% in2e = s2 \set_isin se = true
%%% in3e = s3 \set_isin se = true
%%% in4e = s4 \set_isin se = false
%%% set_notin2 = s2 \set_notin se = false
%%% set_notin3 = s3 \set_notin se = false
%%% set_notin4 = s4 \set_notin se = true

variable_define(in2e, operation(set_isin, (variable(s2),(variable(se),())))).
variable_define(in3e, operation(set_isin, (variable(s3),(variable(se),())))).
variable_define(in4e, operation(set_isin, (variable(s4),(variable(se),())))).
variable_define(set_notin2e, operation(set_notin, (variable(s2),(variable(se),())))).
variable_define(set_notin3e, operation(set_notin, (variable(s3),(variable(se),())))).
variable_define(set_notin4e, operation(set_notin, (variable(s4),(variable(se),())))).
