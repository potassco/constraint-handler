variable_declare(a,fromFacts).
variable_domain(a,val(int,0..1)).
variable_define(b,operation(int_div,(val(int,6),(variable(a),())))).
variable_define(p,operation(add,(variable(a),(variable(f),())))).

forbid_warning(variable(badValue)) :- doit.
{ doit }.
variable_define(f,val(int,10)) :- doit.
variable_define(f,val(int,20)) :- not doit.
