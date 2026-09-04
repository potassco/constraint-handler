variable_define(i,val(int,2)).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

% int-none order comparisons (both directions)
evaluate(operation(lt,(variable(i),(variable(n),())))).
evaluate(operation(lt,(variable(n),(variable(i),())))).
evaluate(operation(leq,(variable(i),(variable(n),())))).
evaluate(operation(leq,(variable(n),(variable(i),())))).
evaluate(operation(gt,(variable(i),(variable(n),())))).
evaluate(operation(gt,(variable(n),(variable(i),())))).
evaluate(operation(geq,(variable(i),(variable(n),())))).
evaluate(operation(geq,(variable(n),(variable(i),())))).

% int-string order comparisons (both directions)
evaluate(operation(lt,(variable(i),(variable(s),())))).
evaluate(operation(lt,(variable(s),(variable(i),())))).
evaluate(operation(leq,(variable(i),(variable(s),())))).
evaluate(operation(leq,(variable(s),(variable(i),())))).
evaluate(operation(gt,(variable(i),(variable(s),())))).
evaluate(operation(gt,(variable(s),(variable(i),())))).
evaluate(operation(geq,(variable(i),(variable(s),())))).
evaluate(operation(geq,(variable(s),(variable(i),())))).
