{ hello }.
variable_define(a,operation(set_make,(val(int,2),()))) :- hello.
set_declare(a) :- not hello.
set_assign(a,val(int,2)) :- not hello.
