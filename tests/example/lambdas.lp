multimap_declare(a).
multimap_assign(a,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(a,val(symbol,width),val(int,2)).
multimap_assign(a,val(symbol,height),val(int,3)).

multimap_declare(b).
multimap_assign(b,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(b,val(symbol,width),val(int,5)).
multimap_assign(b,val(symbol,height),val(int,4)).

multimap_declare(c).
multimap_assign(c,val(symbol,kind),val(symbol,square)).
multimap_assign(c,val(symbol,side),val(int,5)).

multimap_declare(d).
multimap_assign(d,val(symbol,kind),val(symbol,circle)).
multimap_assign(d,val(symbol,radius),val(int,4)).

multimap_declare(e).
multimap_assign(e,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(e,val(symbol,width),val(int,1)).
multimap_assign(e,val(symbol,height),val(int,1)).

set_declare(shapes).
set_assign(shapes,variable(S)) :- S=(a;b;c;d;e).

variable_define(nb_squares,E) :-
  E    = operation(set_fold,(LAMB,(SET,(START,())))),
  SET  = variable(shapes),
  ACCU = variable(accu),
  START= val(int,0),
  VARS = (shape,(accu,())),
  SHAP = variable(shape),
  KIND = operation(find,(val(symbol,kind),(SHAP,()))),
  WIDT = operation(find,(val(symbol,width),(SHAP,()))),
  HEIG = operation(find,(val(symbol,height),(SHAP,()))),
  SQUA = operation(eq,(KIND,(operation(set_make,(val(symbol,square),())),()))),
  RECT = operation(eq,(KIND,(operation(set_make,(val(symbol,rectangle),())),()))),
  SREC = operation(conj,(RECT,(operation(eq,(WIDT,(HEIG,()))),()))),
  ISSQ = operation(disj,(SQUA,(SREC,()))),
  MONE = operation(ite,(ISSQ,(val(int,1),(val(int,0),())))),
  PLUS = operation(add,(MONE,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

define(isSquare,(shape,()),ISSQ) :-
  SHAP = variable(shape),
  KIND = operation(find,(val(symbol,kind),(SHAP,()))),
  WIDT = operation(find,(val(symbol,width),(SHAP,()))),
  HEIG = operation(find,(val(symbol,height),(SHAP,()))),
  SQUA = operation(eq,(KIND,(operation(set_make,(val(symbol,square),())),()))),
  RECT = operation(eq,(KIND,(operation(set_make,(val(symbol,rectangle),())),()))),
  SREC = operation(conj,(RECT,(operation(eq,(WIDT,(HEIG,()))),()))),
  ISSQ = operation(disj,(SQUA,(SREC,()))).

evaluate(variable(isSquare),(variable(a),())).
evaluate(variable(isSquare),(variable(b),())).
evaluate(variable(isSquare),(variable(c),())).
evaluate(variable(isSquare),(variable(d),())).
evaluate(variable(isSquare),(variable(e),())).

variable_define(nb_squares2,E) :-
  E    = operation(set_fold,(LAMB,(SET,(START,())))),
  SET  = variable(shapes),
  ACCU = variable(accu),
  START= val(int,0),
  VARS = (shape,(accu,())),
  SHAP = variable(shape),
  ISSQ = operation(variable(isSquare),(SHAP,())),
  MONE = operation(ite,(ISSQ,(val(int,1),(val(int,0),())))),
  PLUS = operation(add,(MONE,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

#show value/2.
#show _ge_eval_exec/3.
#show warning/3.
