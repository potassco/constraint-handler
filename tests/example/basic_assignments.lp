#include "includeAll.lp".

assign(assign_b, b, val(bool,true)).
assign(assign_i, i, val(int,42)).
assign(assign_f, f, val(float,float("47.1"))).
assign(assign_s, s, val(str,"foo")).
assign(assign_x, x, variable(s)).
assign(assign_y, y, operation(add,(operation(mult,(val(int,2),
                                                  (variable(i), ()))),
                                  (val(int,1), ())))).

%#show direct_query/1.
