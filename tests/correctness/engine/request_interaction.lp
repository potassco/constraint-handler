variable_define(base_c, base_compile, val(int, 1)).
variable_define(base_g, base_ground, val(int, 1)).

requestEngine(base_c, compile).
requestEngine(base_g, ground).


variable_define(c_to_g, compile_to_ground, operation(add, (variable(base_compile), (variable(base_compile),())))).
variable_define(g_to_c, ground_to_compile, operation(add, (variable(base_ground), (variable(base_ground),())))).

requestEngine(c_to_g, ground).
requestEngine(g_to_c, compile).

variable_define(mixed_to_g, mixed_to_ground, operation(add, (variable(base_compile), (variable(base_ground),())))).
variable_define(mixed_to_c, mixed_to_compile, operation(add, (variable(base_compile), (variable(base_ground),())))).

requestEngine(mixed_to_g, ground).
requestEngine(mixed_to_c, compile).
