variable_declare(sym_a,fromFacts).
variable_domain(sym_a,val(symbol,a)).

variable_declare(sym_b,fromFacts).
variable_domain(sym_b,val(symbol,b)).

variable_declare(none_case,fromFacts).
variable_domain(none_case,val(none,none)).

variable_declare(bad_case,fromFacts).
variable_domain(bad_case,bad).

evaluate(gt,(variable(sym_a),(variable(sym_a),()))).
evaluate(gt,(variable(sym_a),(variable(sym_b),()))).
evaluate(gt,(variable(sym_b),(variable(sym_a),()))).
evaluate(gt,(variable(none_case),(variable(sym_a),()))).
evaluate(gt,(variable(sym_a),(variable(none_case),()))).
evaluate(gt,(variable(sym_a),(variable(bad_case),()))).

#show evaluated/3.
