variable_declare(choose_left,boolDomain).

_passed(ssa,left,variable_declare(x,fromFacts,variable(choose_left))).
_passed(ssa,right,variable_declare(x,fromFacts,operation(lnot,(variable(choose_left),())))).
_passed(ssa,left,variable_domain(x,val(int,1),variable(choose_left))).
_passed(ssa,right,variable_domain(x,val(int,2),operation(lnot,(variable(choose_left),())))).

#show value/2.
#show warning/3.
