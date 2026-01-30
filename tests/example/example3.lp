%%% i=42.0                default
%%% f=47.1                default
%%% y= 2i+1               ground
%%% z=y-f                 compile
%%% t=python(math.cos)(z) default
%%% u=sin(z)              ground
variable_define(assign_i, i, val(float,float("42"))).
variable_define(assign_f, f, val(float,float("47.1"))).
variable_define(assign_y, y, operation(add,(operation(mult,(val(int,2),
                                                           (variable(i), ()))),
                                       (val(int,1), ())))).
variable_define(assign_z, z, operation(sub,(variable(y),
                                        (variable(f), ())))).
variable_define(assign_t, t, operation(python("math.cos"),(variable(z),()))).
variable_define(assign_u, u, operation(sin,(variable(z),()))).

requestEngine(assign_y,ground).
requestEngine(assign_z,compile).
%requestEngine(assign_t,ground).
requestEngine(assign_u,ground).
