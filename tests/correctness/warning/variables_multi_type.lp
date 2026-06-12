{ hello }.
variable_define(a,operation(set_make,(val(int,2),()))) :- hello.
variable_declare(a,set) :- not hello.
set_assign(a,val(int,2)) :- not hello.
