%%%%%%%%%%%%%%%%% check if well-formed
_passed(sugar,bool_evaluate(LBL,E)) :- _passed(defaultArgs,bool_evaluate(LBL,E)).
_passed(sugar,ensure(LBL,E)) :- _passed(defaultArgs,ensure(LBL,E)).
_passed(sugar,evaluate(LBL,OP,ARGS)) :- _passed(defaultArgs,evaluate(LBL,OP,ARGS)).


%%%%%% variable atoms
_passed(sugar,variable_declare(LBL,X,definition)) :- _passed(defaultArgs,variable_define(LBL,X,E)).
_passed(sugar,variable_define(LBL,X,E)) :- _passed(defaultArgs,variable_define(LBL,X,E)).

_passed(sugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_declare(LBL,X,D)), D=(boolDomain;definition;fromFacts;fromList(L)).
_passed(sugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_passed(sugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_declare(LBL,X,fromList(L))), E=@pythonListElements(L).
_passed(sugar,variable_domain(LBL,X,val(bool,(false;true)))) :- _passed(defaultArgs,variable_declare(LBL,X,boolDomain)).
_passed(sugar,variable_domain(LBL,X,val(none,none))) :- _passed(defaultArgs,variable_declareOptional(LBL,X)).
_passed(sugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_expression(sugar,val(bool,(false;true))) :- _passed(defaultArgs,variable_declare(LBL,X,boolDomain)).
_expression(sugar,val(none,none)) :- _passed(defaultArgs,variable_declareOptional(LBL,X)).


%%%%%% multimap atoms
_passed(sugar,variable_declare(LBL,X,multimap)) :- _passed(defaultArgs,multimap_declare(LBL,X)).
_passed(sugar,multimap_assign(LBL,X,EKEY,EVAL)) :- _passed(defaultArgs,multimap_assign(LBL,X,EKEY,EVAL)).


%%%%%% set atoms
_passed(sugar,variable_declare(LBL,X,set)) :- _passed(defaultArgs,set_declare(LBL,X)).
_passed(sugar,set_assign(LBL,X,E)) :- _passed(defaultArgs,set_assign(LBL,X,E)).
_passed(sugar,set_baseDomain(LBL,X,E)) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)).


%%%%%% optimize atoms
_passed(sugar,optimize_precision(LBL,PREC,PRIO)) :- _passed(defaultArgs,optimize_precision(LBL,PREC,PRIO)).
_passed(sugar,optimize_maximizeSum(LBL,E,X,P)) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)).

%%%%%% preference atoms
_passed(sugar,preference_holds(LBL,operation(eq,(variable(X),(E,()))),K)) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K > 0.
_passed(sugar,preference_holds(LBL,operation(neq,(variable(X),(E,()))),-K)) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K < 0.
_passed(sugar,preference_holds(LBL,E,K)) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K > 0.
_passed(sugar,preference_holds(LBL,operation(wnot,(E,())),-K)) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.
_expression(sugar,operation(wnot,(E,()))) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.


_expression(sugar,operation(eq,(variable(X),(E,())))) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K > 0.
_expression(sugar,operation(neq,(variable(X),(E,())))) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K < 0.
_expression(sugar,operation(wnot,(E,()))) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.


%%%%%% ssa atoms
_passed(sugar,DEC) :- _passed(ssa,DEC).
_variable(sugar,X) :- _variable(ssa,X).


%%%%%% warning atoms
_passed(sugar,warning_forbid(LBL,KIND)) :- _passed(defaultArgs,warning_forbid(LBL,KIND)).
_passed(sugar,warning_ignore(LBL,KIND)) :- _passed(defaultArgs,warning_ignore(LBL,KIND)).
