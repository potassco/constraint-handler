variable_define(i,val(int,2)).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

% int-none order comparisons (both directions)
evaluate(lt,(variable(i),(variable(n),()))).
evaluate(lt,(variable(n),(variable(i),()))).
evaluate(leq,(variable(i),(variable(n),()))).
evaluate(leq,(variable(n),(variable(i),()))).
evaluate(gt,(variable(i),(variable(n),()))).
evaluate(gt,(variable(n),(variable(i),()))).
evaluate(geq,(variable(i),(variable(n),()))).
evaluate(geq,(variable(n),(variable(i),()))).

% int-string order comparisons (both directions)
evaluate(lt,(variable(i),(variable(s),()))).
evaluate(lt,(variable(s),(variable(i),()))).
evaluate(leq,(variable(i),(variable(s),()))).
evaluate(leq,(variable(s),(variable(i),()))).
evaluate(gt,(variable(i),(variable(s),()))).
evaluate(gt,(variable(s),(variable(i),()))).
evaluate(geq,(variable(i),(variable(s),()))).
evaluate(geq,(variable(s),(variable(i),()))).