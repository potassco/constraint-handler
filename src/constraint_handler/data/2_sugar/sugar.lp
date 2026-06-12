%%%%%%%%%%%%%%%%% check if well-formed
_passed(sugar,LBL,bool_evaluate(E)) :- _passed(defaultArgs,LBL,bool_evaluate(E)).
_passed(sugar,LBL,ensure(E)) :- _passed(defaultArgs,LBL,ensure(E)).
_passed(sugar,LBL,evaluate(OP,ARGS)) :- _passed(defaultArgs,LBL,evaluate(OP,ARGS)).


%%%%%% variable atoms
_passed(sugar,LBL,variable_declare(X,definition)) :- _passed(defaultArgs,LBL,variable_define(X,E)).
_passed(sugar,LBL,variable_define(X,E)) :- _passed(defaultArgs,LBL,variable_define(X,E)).

_passed(sugar,LBL,variable_declare(X,fromFacts)) :- _passed(defaultArgs,LBL,variable_declare(X,D)), D=(boolDomain;definition;fromFacts;fromList(L)).
_passed(sugar,LBL,variable_declare(X,D)) :- _passed(defaultArgs,LBL,variable_declare(X,D)), D=(set;multimap).
_passed(sugar,LBL,variable_domain(X,E)) :- _passed(defaultArgs,LBL,variable_domain(X,E)).
_passed(sugar,LBL,variable_domain(X,E)) :- _passed(defaultArgs,LBL,variable_declare(X,fromList(L))), E=@pythonListElements(L).
_passed(sugar,LBL,variable_domain(X,val(bool,(false;true)))) :- _passed(defaultArgs,LBL,variable_declare(X,boolDomain)).
_passed(sugar,LBL,variable_domain(X,val(none,none))) :- _passed(defaultArgs,LBL,variable_declareOptional(X)).
_passed(sugar,LBL,variable_domain(X,E)) :- _passed(defaultArgs,LBL,variable_domain(X,E)).
_expression(sugar,val(bool,(false;true))) :- _passed(defaultArgs,LBL,variable_declare(X,boolDomain)).
_expression(sugar,val(none,none)) :- _passed(defaultArgs,LBL,variable_declareOptional(X)).


%%%%%% multimap atoms
_passed(sugar,LBL,variable_declare(X,multimap)) :- _passed(defaultArgs,LBL,multimap_declare(X)).
_passed(sugar,LBL,multimap_assign(X,EKEY,EVAL)) :- _passed(defaultArgs,LBL,multimap_assign(X,EKEY,EVAL)).


%%%%%% set atoms
_passed(sugar,LBL,variable_declare(X,set)) :- _passed(defaultArgs,LBL,set_declare(X)).
_passed(sugar,LBL,set_assign(X,E)) :- _passed(defaultArgs,LBL,set_assign(X,E)).
_passed(sugar,LBL,set_baseDomain(X,E)) :- _passed(defaultArgs,LBL,set_baseDomain(X,E)).


%%%%%% optimize atoms
_passed(sugar,LBL,optimize_precision(PREC,PRIO)) :- _passed(defaultArgs,LBL,optimize_precision(PREC,PRIO)).
_passed(sugar,LBL,optimize_maximizeSum(E,X,P)) :- _passed(defaultArgs,LBL,optimize_maximizeSum(E,X,P)).

%%%%%% preference atoms
_passed(sugar,LBL,preference_holds(operation(eq,(variable(X),(E,()))),K)) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K)), K > 0.
_passed(sugar,LBL,preference_holds(operation(neq,(variable(X),(E,()))),-K)) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K)), K < 0.
_passed(sugar,LBL,preference_holds(E,K)) :- _passed(defaultArgs,LBL,preference_holds(E,K)), K > 0.
_passed(sugar,LBL,preference_holds(operation(wnot,(E,())),-K)) :- _passed(defaultArgs,LBL,preference_holds(E,K)), K < 0.
_expression(sugar,operation(wnot,(E,()))) :- _passed(defaultArgs,LBL,preference_holds(E,K)), K < 0.


_expression(sugar,operation(eq,(variable(X),(E,())))) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K)), K > 0.
_expression(sugar,operation(neq,(variable(X),(E,())))) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K)), K < 0.
_expression(sugar,operation(wnot,(E,()))) :- _passed(defaultArgs,LBL,preference_holds(E,K)), K < 0.


%%%%%% ssa atoms
_passed(sugar,LBL,DEC) :- _passed(ssa,LBL,DEC).
_variable(sugar,X) :- _variable(ssa,X).


%%%%%% warning atoms
_passed(sugar,LBL,warning_forbid(KIND)) :- _passed(defaultArgs,LBL,warning_forbid(KIND)).
_passed(sugar,LBL,warning_ignore(KIND)) :- _passed(defaultArgs,LBL,warning_ignore(KIND)).

%%%%%% interface variables
_variable_execution_outputVar(X) :- _passed(ssa,LBL,variable_declare(X,DECL)), X=execution_output(PRG,VAR).
_variable_internal(X) :- _passed(ssa,LBL,variable_declare(X,DECL)), not _variable_execution_outputVar(X).
_passed(sugar,LBL,variable_interface(X)) :- _passed(sugar,LBL,variable_declare(X,DECL)), not _variable_internal(X).
