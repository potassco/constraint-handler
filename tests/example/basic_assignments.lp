#include "includeAll.lp".

assign(assign_b, b, constant(bool(true))).
assign(assign_i, i, constant(int(42))).
assign(assign_f, f, constant(float("47.1"))).
assign(assign_s, s, constant(str("foo"))).
assign(assign_x, x, variable(s)).
assign(assign_y, y, operation(add,(operation(mult,(constant(int(2)),
                                                  (variable(i), ()))),
                                  (constant(int(1)), ())))).

%#show expression/1.
