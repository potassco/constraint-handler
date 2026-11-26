{ choose }.
variable_define(s,operation(set_make,(val(int,1),()))) :- choose.
variable_define(s,operation(set_make,(val(int,2),()))) :- not choose.
