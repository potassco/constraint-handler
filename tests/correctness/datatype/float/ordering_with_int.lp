%%% float/float and float/int comparison checks
variable_define(f_small,val(float,float("1.5"))).
variable_define(f_large,val(float,float("2.5"))).
variable_define(i_two,val(int,2)).

% float vs float comparisons
evaluate(operation(lt,(variable(f_small),(variable(f_large),())))).
evaluate(operation(leq,(variable(f_small),(variable(f_large),())))).
evaluate(operation(gt,(variable(f_large),(variable(f_small),())))).
evaluate(operation(geq,(variable(f_large),(variable(f_small),())))).
evaluate(operation(eq,(variable(f_small),(variable(f_small),())))).
evaluate(operation(neq,(variable(f_small),(variable(f_large),())))).

% float vs int comparisons
evaluate(operation(lt,(variable(f_small),(variable(i_two),())))).
evaluate(operation(gt,(variable(f_large),(variable(i_two),())))).
evaluate(operation(eq,(variable(i_two),(val(float,float("2.0")),())))).
evaluate(operation(eq,(variable(f_large),(val(int,2),())))).
evaluate(operation(neq,(variable(f_large),(variable(i_two),())))).
evaluate(operation(leq,(variable(i_two),(variable(f_large),())))).
evaluate(operation(geq,(variable(i_two),(variable(f_small),())))).
