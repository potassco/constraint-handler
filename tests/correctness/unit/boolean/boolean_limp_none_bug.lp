% compile2 currently goes UNSAT for these left-none implication cases.


variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(limp,(variable(x),(val(bool,false),())))).
evaluate(operation(limp,(variable(x),(val(none,none),())))).
evaluate(operation(limp,(variable(x),(bad,())))).


evaluate(operation(limp,(val(none,none),(val(bool,false),())))).
evaluate(operation(limp,(val(none,none),(val(none,none),())))).
