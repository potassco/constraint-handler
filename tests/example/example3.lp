#include "includeAll.lp".

%%% i=42.0                default
%%% f=47.1                default
%%% y= 2i+1               ground
%%% z=y-f                 compile
%%% t=python(math.cos)(z) default
%%% u=sin(z)              ground
assign(assign_i, i, val(float,float("42"))).
assign(assign_f, f, val(float,float("47.1"))).
assign(assign_y, y, operation(add,(operation(mult,(val(int,2),
                                                           (variable(i), ()))),
                                       (val(int,1), ())))).
assign(assign_z, z, operation(minus,(variable(y),
                                        (variable(f), ())))).
assign(assign_t, t, operation(python(val(str,"math.cos")),(variable(z),()))).
assign(assign_u, u, operation(sin,(variable(z),()))).

requestEngine(assign_y,ground).
requestEngine(assign_z,compile).
%requestEngine(assign_t,ground).
requestEngine(assign_u,ground).
