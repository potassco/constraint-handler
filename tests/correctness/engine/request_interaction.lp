variable_define(base_compile,val(int,1),base_c).
variable_define(base_ground,val(int,1),base_g).

engine_request(base_c, compile).
engine_request(base_g, ground).


variable_define(compile_to_ground,operation(add,(variable(base_compile),(variable(base_compile),()))),c_to_g).
variable_define(ground_to_compile,operation(add,(variable(base_ground),(variable(base_ground),()))),g_to_c).

engine_request(c_to_g,ground).
engine_request(g_to_c,compile).

variable_define(mixed_to_ground,operation(add,(variable(base_compile),(variable(base_ground),()))),mixed_to_g).
variable_define(mixed_to_compile,operation(add,(variable(base_compile),(variable(base_ground),()))),mixed_to_c).

engine_request(mixed_to_g,ground).
engine_request(mixed_to_c,compile).
