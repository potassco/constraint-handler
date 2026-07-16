% Regression for compile2 emitting multiple stable models with the same projected
% user-visible values when an optional value flows through an equality.

ensure(operation(limp,(operation(hasValue,(variable(execution_output(x,"d")),())),(operation(hasValue,(variable(execution_input(y,"f")),())),())))).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(execution_input(x,"a")),(variable(a),()))),())))).
ensure(operation(limp,(val(bool,true),(operation(eq,(variable(a),(variable(execution_input(x,"a")),()))),())))).
ensure(operation(limp,
                (operation(conj,
                      (operation(hasValue,(variable(execution_input(y,"f")),())),
                      (operation(hasValue,(variable(execution_output(x,"d")),())),()))),
                (operation(eq,(variable(execution_output(x,"d")),(variable(execution_input(y,"f")),()))),())))).

execution_declare(x,
    if(operation(eq,(variable("a"),(val(int,1),()))),
       assign("d",val(int,1)),
       noop),("a",()),("d",())).

execution_declare(y,
    seq2(assign("g",operation(hasValue,(variable("f"),()))),
         if(operation(lnot,
                     (operation(disj,
                               (variable("g"),
                               (operation(lnot,(operation(eq,(variable("e"),(val(int,1),()))),())),()))),())),
             assert(val(bool,false)),
             noop)),("e",("f",())),()).

execution_run(x).
execution_run(y).

variable_declare(a,fromFacts).
variable_domain(a,val(int,0)).
variable_domain(a,val(int,1)).

variable_declare(execution_input(x,"a"),fromFacts).
variable_domain(execution_input(x,"a"),variable(a)).

variable_declare(execution_input(y,"e"),fromFacts).
variable_domain(execution_input(y,"e"),val(int,0)).
variable_domain(execution_input(y,"e"),val(int,1)).

variable_declare(execution_input(y,"f"),fromFacts).
variable_domain(execution_input(y,"f"),val(none,none)).
variable_domain(execution_input(y,"f"),variable(execution_output(x,"d"))).
