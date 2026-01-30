variable_define(assign_b, b, val(bool,true)).
variable_define(assign_i, i, val(int,42)).
variable_define(assign_f, f, val(float,float("47.1"))).
variable_define(assign_s, s, val(str,"foo")).
variable_define(assign_x, x, variable(s)).
variable_define(assign_y, y, operation(add,(operation(mult,(val(int,2),
                                                  (variable(i), ()))),
                                  (val(int,1), ())))).

%#show direct_query/1.
