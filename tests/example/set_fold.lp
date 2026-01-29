#show value/2.
#show set_value/2.

set_declare(d,num_set).
set_assign(d,num_set,val(float,float("3.5"))).
{ set_assign(d,num_set,val(float,float(F))) : F=("1.5";"2.5";"4.5";"5.5") }.


variable_define(d,the_sum,EXPR) :-
  STEP = val(function,add),
  SET = variable(num_set),
  INIT = val(int,0),
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).



%%% we can define the step function separately if we want.
variable_define(d,square_and_add,lambda(VARS,RESULT)) :-
  VARS   = (x,(accu,())),
  VARX   = variable(x),
  SQUARE = operation(mult,(VARX,(VARX,()))),
  RESULT = operation(add,(SQUARE,(variable(accu),()))).

variable_define(d,sum_squares,EXPR) :-
  STEP = variable(square_and_add),
  SET  = variable(num_set),
  INIT = val(int,0),
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).



variable_define(d,manual_count,EXPR) :-
  STEP = lambda((elt,(accu,())),operation(add,(val(int,1),(variable(accu),())))),
  SET = variable(num_set),
  INIT = val(int,0),
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).



variable_define(d,the_max,EXPR) :-
  STEP = val(function,max),
  SET = variable(num_set),
  INIT = val(int,-1000), % #inf is not supported
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).



variable_define(d,any_between_four_five,EXPR) :-
  VAR  = variable(elt),
  FOUR = operation(lt,(val(int,4),(VAR,()))),
  FIVE = operation(lt,(VAR,(val(int,5),()))),
  BETW = operation(conj,(FOUR,(FIVE,()))),
  STEP = lambda((elt,(accu,())),operation(disj,(BETW,(variable(accu),())))),
  SET  = variable(num_set),
  INIT = val(bool,false),
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).



variable_define(d,all_between_two_five,EXPR) :-
  VAR  = variable(elt),
  TWO  = operation(leq,(val(int,2),(VAR,()))),
  FIVE = operation(leq,(VAR,(val(int,5),()))),
  BETW = operation(conj,(TWO,(FIVE,()))),
  STEP = lambda((elt,(accu,())),operation(conj,(BETW,(variable(accu),())))),
  SET = variable(num_set),
  INIT = val(bool,true),
  EXPR = operation(set_fold,(STEP,(SET,(INIT,())))).
