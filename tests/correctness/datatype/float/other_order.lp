variable_define(f,val(float,float("1.5"))).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

% float-none order comparisons (both directions)
evaluate(lt,(variable(f),(variable(n),()))).
evaluate(lt,(variable(n),(variable(f),()))).
evaluate(leq,(variable(f),(variable(n),()))).
evaluate(leq,(variable(n),(variable(f),()))).
evaluate(gt,(variable(n),(variable(f),()))).
evaluate(gt,(variable(f),(variable(n),()))).
evaluate(geq,(variable(f),(variable(n),()))).
evaluate(geq,(variable(n),(variable(f),()))).

% float-string order comparisons (both directions)
evaluate(lt,(variable(f),(variable(s),()))).
evaluate(lt,(variable(s),(variable(f),()))).
evaluate(leq,(variable(f),(variable(s),()))).
evaluate(leq,(variable(s),(variable(f),()))).
evaluate(gt,(variable(f),(variable(s),()))).
evaluate(gt,(variable(s),(variable(f),()))).
evaluate(geq,(variable(f),(variable(s),()))).
evaluate(geq,(variable(s),(variable(f),()))).
