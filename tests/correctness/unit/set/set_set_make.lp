variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).


evaluate(operation(cardinality,(operation(set_make,()),()))).
evaluate(operation(eq,(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),(operation(set_make,(val(none,none),(val(int,2),(val(int,1),())))),())))).
evaluate(operation(set_isin,(val(none,none),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),())))).
evaluate(operation(set_isin,(val(int,3),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),())))).
evaluate(operation(cardinality,(operation(set_make,(bad,(val(int,5),()))),()))).
evaluate(operation(cardinality,(operation(set_make,(variable(x),())),()))).
