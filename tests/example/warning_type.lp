#include "includeAll.lp".

variable_define(assign_b, b, val(bool,true)).
variable_define(assign_i, i, val(int,42)).
variable_define(assign_f, f, val(float,float("47.1"))).
variable_define(assign_s, s, val(str,"foo")).
variable_define(assign_x, x, variable(s)).
variable_define(assign_y, y, operation(add,(operation(mult,(val(int,2),
                                                  (variable(i), ()))),
                                  (val(int,1), ())))).

variable_define(assign_y, z, operation(ite,(variable(b),(variable(i),(variable(y),()))))).

variable_declare(facts, color, fromFacts).
variable_domain(color,val(symbol,(red;green;blue))).
variable_declare(facts, calar, fromList((val(str,"red"),(val(str,"green"),(val(str,"blue"),()))))).

variable_define(bad_type, e1, operation(ite,(variable(x),(variable(i),(variable(y),()))))).
variable_define(bad_type, e2, operation(ite,(variable(b),(variable(s),(variable(y),()))))).
variable_define(undefine, e3, operation(ite,(variable(unk),(variable(s),(variable(y),()))))).

type_query(operation(ite,(variable(i),(variable(i),(variable(i),()))))).
type_query(operation(ite,(variable(b),(variable(i),(variable(i),()))))).

%defaultEngine(none).
%type_query(variable(y)).

#show type_expression/3.
#show type_variable/3.
%#show type_query_variable/2.
#show warning/3.
%#show _variable_exists/2.
