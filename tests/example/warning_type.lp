variable_define(b, val(bool,true)).
variable_define(i, val(int,42)).
variable_define(f, val(float,float("47.1"))).
variable_define(s, val(string,"foo")).
variable_define(x, variable(s)).
variable_define(y, operation(add,(operation(mult,(val(int,2),
                                                  (variable(i), ()))),
                                  (val(int,1), ())))).

variable_define(z, operation(ite,(variable(b),(variable(i),(variable(y),()))))).

variable_declare(color, fromFacts).
variable_domain(color,val(symbol,(red;green;blue))).
variable_declare(calar, fromList((val(string,"red"),(val(string,"green"),(val(string,"blue"),()))))).

variable_define(e1, operation(ite,(variable(x),(variable(i),(variable(y),()))))).
variable_define(e2, operation(ite,(variable(b),(variable(s),(variable(y),()))))).
variable_define(e3, operation(ite,(variable(unk),(variable(s),(variable(y),()))))).

type_query(operation(ite,(variable(i),(variable(i),(variable(i),()))))).
type_query(operation(ite,(variable(b),(variable(i),(variable(i),()))))).

evaluate(eq,(val(bool,true),(val(float,float(14)),()))).
