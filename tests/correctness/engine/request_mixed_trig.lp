%%% Mixed-engine dependency chain with trig evaluation.
%%% i=42.0                default
%%% f=47.1                default
%%% y=2*i+1               ground
%%% z=y-f                 compile
%%% u=sin(z)              ground

variable_define(i,val(float,float("42"))).
variable_define(f,val(float,float("47.1"))).
variable_define(y,operation(add,(operation(mult,(val(int,2),
                                                (variable(i),()))),
                                (val(int,1),()))),assign_y).
variable_define(z,operation(sub,(variable(y),
                                (variable(f),()))),assign_z).
variable_define(u,operation(sin,(variable(z),())),assign_u).

engine_request(assign_y,ground).
engine_request(assign_z,compile).
engine_request(assign_u,ground).
