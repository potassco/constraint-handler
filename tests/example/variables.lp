variable_declare(d_x,x,boolDomain).
variable_define(d_y,y,operation(lnot,(variable(x),()))).
evaluate(neq,(variable(x),(variable(y),()))).

variable_declare(d_vertices,r,fromList((R,()))) :-
  R=val(symbol,red).
variable_declare(d_vertices,g,fromList((R,(G,(B,()))))) :-
  R=val(symbol,red), G=val(symbol,green), B=val(symbol,blue).
variable_declare(d_vertices,b,fromFacts).
variable_domain(b,val(symbol,(red;green;blue))).

variable_declare(d_vertices,p,fromList((R,(G,(B,()))))) :-
  R=val(symbol,red), G=val(symbol,green), B=val(symbol,blue).
variable_declareOptional(p).

ensure(e_bb,operation(eq,(variable(b),(val(symbol,blue),())))).
ensure(e_rg,operation(neq,(variable(r),(variable(g),())))).
ensure(e_gb,operation(neq,(variable(g),(variable(b),())))).

ensure(e_rp,operation(neq,(variable(r),(variable(p),())))).
ensure(e_gp,operation(neq,(variable(g),(variable(p),())))).
ensure(e_bp,operation(neq,(variable(b),(variable(p),())))).

variable_define(d_s,g_is_green,operation(eq,(variable(g),(val(symbol,green),())))).
