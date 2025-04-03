#include "includeAll.lp".

%%% i=42.0                default
%%% f=47.1                default
%%% y= 2i+1               ground
%%% z=y-f                 compile
%%% t=python(math.cos)(z) default
%%% u=sin(z)              ground
assign(assign_i, i, constant(float("42"))).
assign(assign_f, f, constant(float("47.1"))).
assign(assign_y, y, operation(add,(operation(mult,(constant(int(2)),
                                                           (variable(i), ()))),
                                       (constant(int(1)), ())))).
assign(assign_z, z, operation(minus,(variable(y),
                                        (variable(f), ())))).
assign(assign_t, t, operation(python(constant(str("math.cos"))),(variable(z),()))).
assign(assign_u, u, operation(sin,(variable(z),()))).

requestEngine(assign_y,ground).
requestEngine(assign_z,compile).
%requestEngine(assign_t,ground).
requestEngine(assign_u,ground).
