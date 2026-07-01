variable_define(pool,operation(set_make,(val(int,1),(val(int,2),(val(int,3),()))))).
variable_define(has_two,operation(python("lambda pool: 2 in pool"),(variable(pool),()))).
variable_define(missing_four,operation(python("lambda pool: 4 not in pool"),(variable(pool),()))).

phase_request(type_check,false).
