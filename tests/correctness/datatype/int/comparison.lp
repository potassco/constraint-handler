%%% int comparison checks only (minus/division/power are covered in dedicated files)
%%% 12==12     not 20!=20     not -8==8
%%% 2<=10     2<10     not 2>=10     not 2>10
%%% 12<=12     not 12<12     12>=12     not 12>12
%%% 6//2==3   5//2==2
%%% 6/2==3.0  5/2==2.5
%%% 1==1.0    not 1!=1.0

evaluate(eq,(val(int,12),(val(int,12),()))).
evaluate(neq,(val(int,20),(val(int,20),()))).
evaluate(eq,(val(int,-8),(val(int,8),()))).
evaluate(leq,(val(int,2),(val(int,10),()))).
evaluate(lt,(val(int,2),(val(int,10),()))).
evaluate(geq,(val(int,2),(val(int,10),()))).
evaluate(gt,(val(int,2),(val(int,10),()))).
evaluate(leq,(val(int,12),(val(int,12),()))).
evaluate(lt,(val(int,12),(val(int,12),()))).
evaluate(geq,(val(int,12),(val(int,12),()))).
evaluate(gt,(val(int,12),(val(int,12),()))).
evaluate(eq,(operation(int_div,(val(int,6),(val(int,2),()))),(val(int,3),()))).
evaluate(eq,(operation(int_div,(val(int,5),(val(int,2),()))),(val(int,2),()))).
evaluate(eq,(operation(float_div,(val(int,6),(val(int,2),()))),(val(float,float("3.0")),()))).
evaluate(eq,(operation(float_div,(val(int,5),(val(int,2),()))),(val(float,float("2.5")),()))).
evaluate(eq,(val(int,1),(val(float,float("1.0")),()))).
evaluate(neq,(val(int,1),(val(float,float("1.0")),()))).
