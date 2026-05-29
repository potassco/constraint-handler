execution_declare(prg,TOTA,(cond,()),(x,())) :-
  TOTA=seq2(ZERO,ITEL),
  ITEL=if(variable(cond),STMT,noop),
  STMT=seq2(seq2(ZERO,PLUS),seq2(PLUS,PLUS)),
  ZERO=assign(x,val(int,0)),
  PLUS=assign(x,operation(add,(variable(x),(val(int,1),())))).
execution_run(prg).

variable_declare(execution_input(prg,cond),boolDomain).
