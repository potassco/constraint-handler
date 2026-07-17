variable_define(f_small,val(float,float("1.5"))).
variable_define(f_large,val(float,float("2.5"))).
variable_define(i_two,val(int,2)).

% float vs float comparisons
evaluate(lt,(variable(f_small),(variable(f_large),()))).
evaluate(leq,(variable(f_small),(variable(f_large),()))).
evaluate(gt,(variable(f_large),(variable(f_small),()))).
evaluate(geq,(variable(f_large),(variable(f_small),()))).
evaluate(eq,(variable(f_small),(variable(f_small),()))).
evaluate(neq,(variable(f_small),(variable(f_large),()))).

% float vs int comparisons
evaluate(lt,(variable(f_small),(variable(i_two),()))).
evaluate(gt,(variable(f_large),(variable(i_two),()))).
evaluate(eq,(variable(i_two),(val(float,float("2.0")),()))).
evaluate(eq,(variable(f_large),(val(int,2),()))).
evaluate(neq,(variable(f_large),(variable(i_two),()))).
evaluate(leq,(variable(i_two),(variable(f_large),()))).
evaluate(geq,(variable(i_two),(variable(f_small),()))).
