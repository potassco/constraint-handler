variable_define(a,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(b,operation(set_make,(val(int,2),(val(int,3),(val(int,4),()))))).
variable_define(c,operation(set_make,(val(int,2),(val(int,4),())))).
variable_define(empty,operation(set_make,())).

variable_define(unary,operation(inter,(variable(a),()))).
variable_define(unary_empty,operation(inter,(variable(empty),()))).
variable_define(ternary,operation(inter,(variable(a),(variable(b),(variable(c),()))))).
variable_define(quaternary_empty,operation(inter,(variable(a),(variable(b),(variable(c),(variable(empty),())))))).

variable_define(len_unary,operation(cardinality,(variable(unary),()))).
variable_define(len_unary_empty,operation(cardinality,(variable(unary_empty),()))).
variable_define(len_ternary,operation(cardinality,(variable(ternary),()))).
variable_define(len_quaternary_empty,operation(cardinality,(variable(quaternary_empty),()))).
