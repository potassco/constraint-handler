define(dmf,myfactorial,(n,()),EXP) :-
  VAR = variable(n),
  ONE = val(int,1),
  MIN = operation(sub,(VAR,(ONE,()))),
  REC = operation(variable(myfactorial),(MIN,())),
  PRO = operation(mult,(VAR,(REC,()))),
  EQ1 = operation(leq,(VAR,(ONE,()))),
  EXP = operation(ite,(EQ1,(ONE,(PRO,())))).

evaluate(variable(myfactorial),(val(int,5),())).
