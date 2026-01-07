#include "includeAll.lp".

multimap_declare(dummy,a).
multimap_assign(dummy,a,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(dummy,a,val(symbol,width),val(int,2)).
multimap_assign(dummy,a,val(symbol,height),val(int,3)).

multimap_declare(dummy,b).
multimap_assign(dummy,b,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(dummy,b,val(symbol,width),val(int,5)).
multimap_assign(dummy,b,val(symbol,height),val(int,4)).

multimap_declare(dummy,c).
multimap_assign(dummy,c,val(symbol,kind),val(symbol,square)).
multimap_assign(dummy,c,val(symbol,side),val(int,5)).

multimap_declare(dummy,d).
multimap_assign(dummy,d,val(symbol,kind),val(symbol,circle)).
multimap_assign(dummy,d,val(symbol,radius),val(int,4)).

multimap_declare(dummy,e).
multimap_assign(dummy,e,val(symbol,kind),val(symbol,rectangle)).
multimap_assign(dummy,e,val(symbol,width),val(int,1)).
multimap_assign(dummy,e,val(symbol,height),val(int,1)).

set_declare(d_s,shapes).
set_assign(a_s,shapes,variable(S)) :- S=(a;b;c;d;e).

variable_define(dummy,nb_squares,E) :-
  E    = operation(set_fold,(LAMB,(SET,(START,())))),
  SET  = variable(shapes),
  ACCU = variable(accu),
  START= val(int,0),
  VARS = (shape,(accu,())),
  SHAP = variable(shape),
  KIND = operation(find,(val(symbol,kind),(SHAP,()))),
  WIDT = operation(find,(val(symbol,width),(SHAP,()))),
  HEIG = operation(find,(val(symbol,height),(SHAP,()))),
  SQUA = operation(eq,(KIND,(operation(makeSet,(val(symbol,square),())),()))),
  RECT = operation(eq,(KIND,(operation(makeSet,(val(symbol,rectangle),())),()))),
  SREC = operation(conj,(RECT,(operation(eq,(WIDT,(HEIG,()))),()))),
  ISSQ = operation(disj,(SQUA,(SREC,()))),
  MONE = operation(ite,(ISSQ,(val(int,1),(val(int,0),())))),
  PLUS = operation(add,(MONE,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

define(dis,isSquare,(shape,()),ISSQ) :-
  SHAP = variable(shape),
  KIND = operation(find,(val(symbol,kind),(SHAP,()))),
  WIDT = operation(find,(val(symbol,width),(SHAP,()))),
  HEIG = operation(find,(val(symbol,height),(SHAP,()))),
  SQUA = operation(eq,(KIND,(operation(makeSet,(val(symbol,square),())),()))),
  RECT = operation(eq,(KIND,(operation(makeSet,(val(symbol,rectangle),())),()))),
  SREC = operation(conj,(RECT,(operation(eq,(WIDT,(HEIG,()))),()))),
  ISSQ = operation(disj,(SQUA,(SREC,()))).

evaluate(variable(isSquare),(variable(a),())).
evaluate(variable(isSquare),(variable(b),())).
evaluate(variable(isSquare),(variable(c),())).
evaluate(variable(isSquare),(variable(d),())).
evaluate(variable(isSquare),(variable(e),())).

variable_define(dummy,nb_squares2,E) :-
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

#show value/3.
#show _ge_eval_exec/3.
