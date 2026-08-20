phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).


evaluate(cardinality,(operation(set_make,()),())).
evaluate(eq,(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),(operation(set_make,(val(none,none),(val(int,2),(val(int,1),())))),()))).
evaluate(set_isin,(val(none,none),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),()))).
evaluate(set_isin,(val(int,3),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),()))).
evaluate(cardinality,(operation(set_make,(bad,(val(int,5),()))),())).
evaluate(cardinality,(operation(set_make,(variable(x),())),())).
