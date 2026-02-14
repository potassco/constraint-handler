%%%% x = 0
%%%% if cond:
%%%%     x = 1
%%%% y = x
%%%% z = y == 1 or y == 0

%%%% x0 = 0
%%%% if cond:
%%%%     x1 = 1
%%%% y0 = default(x1,x0)
%%%% z = y0 == 1 or y0 == 0

%%%% { a := 0; a := 1 } 1
%%%% hasValue(a) iff default negation (not a)
%%%% hasValue(a) iff hasValue(not a)
%%%% hasValue(a) iff hasValue(not a)
%%% all:
%%% hasValue(a) iff default(a < 2,false)
%%% any:
%%% hasValue(a)==true     hasValue(a)==false

variable_declare(a_c,cond,boolDomain).
variable_declareOptional(cond).
variable_define(assign_x0,x0,val(int,0)).
variable_define(assign_x1,x1,operation(if,(variable(cond),(val(int,1),())))).
variable_define(assign_y0,y0,operation(default,(variable(x1),(variable(x0),())))).
variable_define(assign_z,z,operation(disj,
                             (operation(eq, (variable(y0), (val(int,1),()))),
                             (operation(eq, (variable(y0), (val(int,0),()))),())))).

variable_declare(conditionals,a,fromFacts).
variable_domain(a,(val(int,0..1);val(none,none))).
evaluate(hasValue,(variable(a),())).
evaluate(leqv,(operation(hasValue,(variable(a),())),
             (operation(leq,(operation(default,(variable(a),(val(int,20),()))),(val(int,3),()))),
             ()))).