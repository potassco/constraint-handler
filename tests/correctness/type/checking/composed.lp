phase_request(type_check,true).

variable_declare(v_int,fromFacts).
variable_domain(v_int,val(int,3)).
variable_declare(v_float,fromFacts).
variable_domain(v_float,val(float,float("3.14"))).
variable_declare(v_string,fromFacts).
variable_domain(v_string,val(string,"s")).
variable_declare(v_symbol,fromFacts).
variable_domain(v_symbol,val(symbol,some_symbol)).

variable_define(c_multimap_make_empty,operation(multimap_make,())).

variable_define(c_length_find_multimap_make,operation(length,(SET,()))) :-
    SET = operation(find,(KEY,(MAP,()))),
    MAP = operation(multimap_make,(ITEM1,(ITEM2,(ITEM3,())))),
    KEY = variable(v_string),
    ITEM1 = (KEY,variable(v_int)),
    ITEM2 = (KEY,variable(v_float)),
    KEY2 = variable(v_symbol),
    ITEM3 = (KEY2,variable(v_int)).
