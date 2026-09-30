variable_define(base_compile,val(int,1),base_c).
variable_define(base_ground,val(int,1),base_g).

engine_request(compile,base_c).
engine_request(ground,base_g).


variable_define(compile_to_ground,operation(add,(variable(base_compile),(variable(base_compile),()))),c_to_g).
variable_define(ground_to_compile,operation(add,(variable(base_ground),(variable(base_ground),()))),g_to_c).

engine_request(ground,c_to_g).
engine_request(compile,g_to_c).

variable_define(mixed_to_ground,operation(add,(variable(base_compile),(variable(base_ground),()))),mixed_to_g).
variable_define(mixed_to_compile,operation(add,(variable(base_compile),(variable(base_ground),()))),mixed_to_c).

engine_request(ground,mixed_to_g).
engine_request(compile,mixed_to_c).
