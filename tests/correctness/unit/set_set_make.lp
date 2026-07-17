variable_declare(bad_arg,fromFacts).
variable_domain(bad_arg,bad).

evaluate(length,(operation(set_make,()),())).
evaluate(eq,(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),(operation(set_make,(val(none,none),(val(int,2),(val(int,1),())))),()))).
evaluate(set_isin,(val(none,none),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),()))).
evaluate(set_isin,(val(int,3),(operation(set_make,(val(int,1),(val(int,2),(val(int,1),(val(none,none),()))))),()))).
evaluate(length,(operation(set_make,(variable(bad_arg),(val(int,5),()))),())).

#show evaluated/3.
