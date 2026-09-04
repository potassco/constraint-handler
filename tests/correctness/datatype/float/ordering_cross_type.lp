%%% float compared with none/string for order operators
variable_define(f,val(float,float("1.5"))).
variable_define(n,val(none,none)).
variable_define(s,val(string,"x")).

% float-none order comparisons (both directions)
evaluate(operation(lt,(variable(f),(variable(n),())))).
evaluate(operation(lt,(variable(n),(variable(f),())))).
evaluate(operation(leq,(variable(f),(variable(n),())))).
evaluate(operation(leq,(variable(n),(variable(f),())))).
evaluate(operation(gt,(variable(n),(variable(f),())))).
evaluate(operation(gt,(variable(f),(variable(n),())))).
evaluate(operation(geq,(variable(f),(variable(n),())))).
evaluate(operation(geq,(variable(n),(variable(f),())))).

% float-string order comparisons (both directions)
evaluate(operation(lt,(variable(f),(variable(s),())))).
evaluate(operation(lt,(variable(s),(variable(f),())))).
evaluate(operation(leq,(variable(f),(variable(s),())))).
evaluate(operation(leq,(variable(s),(variable(f),())))).
evaluate(operation(gt,(variable(f),(variable(s),())))).
evaluate(operation(gt,(variable(s),(variable(f),())))).
evaluate(operation(geq,(variable(f),(variable(s),())))).
evaluate(operation(geq,(variable(s),(variable(f),())))).
