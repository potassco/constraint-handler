variable_define(b, val(bool,true)).
variable_define(i, val(int,42)).
variable_define(f, val(float,float("47.1"))).
variable_define(s, val(string,"foo")).
variable_define(x, variable(s)).
variable_define(y, operation(add,(operation(mult,(val(int,2),
                                                  (variable(i), ()))),
                                  (val(int,1), ())))).

%#show direct_query/1.
