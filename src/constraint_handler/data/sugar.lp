_passed(sugar,bool_evaluate(LBL,E)) :- not _main(wf_check), _passed(presugar,bool_evaluate(LBL,E)).

_expression(presugar,E) :- _expression(defaultArgs,E).

%%%%%%%%%%%%%%%%% check if well-formed
_passed(presugar,bool_evaluate(LBL,E)) :- _passed(defaultArgs,bool_evaluate(LBL,E)).
_passed(presugar,ensure(LBL,E)) :- _passed(defaultArgs,ensure(LBL,E)).
_passed(presugar,evaluate(LBL,OP,ARGS)) :- _passed(defaultArgs,evaluate(LBL,OP,ARGS)).


%%%%%% variable atoms
_passed(presugar,variable_declare(LBL,X,definition)) :- _passed(defaultArgs,variable_define(LBL,X,E)).
_passed(presugar,variable_define(LBL,X,E)) :- _passed(defaultArgs,variable_define(LBL,X,E)).

_passed(presugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_declare(LBL,X,D)), D=(boolDomain;definition;fromFacts;fromList(L)).
_passed(presugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_passed(presugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_declare(LBL,X,fromList(L))), E=@pythonListElements(L).
_passed(presugar,variable_domain(LBL,X,val(bool,(false;true)))) :- _passed(defaultArgs,variable_declare(LBL,X,boolDomain)).
_passed(presugar,variable_domain(LBL,X,val(none,none))) :- _passed(defaultArgs,variable_declareOptional(LBL,X)).
_passed(presugar,variable_domain(LBL,X,E)) :- _passed(defaultArgs,variable_domain(LBL,X,E)).
_expression(presugar,val(bool,(false;true))) :- _passed(defaultArgs,variable_declare(LBL,X,boolDomain)).
_expression(presugar,val(none,none)) :- _passed(defaultArgs,variable_declareOptional(LBL,X)).

_variable_declared(X) :- _passed(defaultArgs,variable_declare(LBL,X,fromFacts)).
_passed(presugar,variable_declare(LBL,X,fromFacts)) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).
_warning(variable(undeclared),(),X) :- _passed(defaultArgs,variable_domain(LBL,X,E)), not _variable_declared(X).

_warning(variable(multipleDeclarations),(CNAME1,(CNAME2,())),(X,D1,D2)) :-
  _passed(defaultArgs,variable_declare(CNAME1,X,D1)), _passed(defaultArgs,variable_declare(CNAME2,X,D2)), (CNAME1,D1) < (CNAME2,D2),
  0 = #count { CNAME3,D3 : _passed(defaultArgs,variable_declare(CNAME3,X,D3)), (CNAME3,D3) < (CNAME2,D2), (CNAME3,D3) != (CNAME1,D1) }.

_warning(variable(multipleDefinitions),(CNAME1,(CNAME2,())),(X,E1,E2)) :-
  _passed(defaultArgs,variable_define(CNAME1,X,E1)), _passed(defaultArgs,variable_define(CNAME2,X,E2)), (CNAME1,E1) < (CNAME2,E2),
  0 = #count { CNAME3,E3 : _passed(defaultArgs,variable_define(CNAME3,X,E3)), (CNAME3,E3) < (CNAME2,E2), (CNAME3,E3) != (CNAME1,E1) }.



%%%%%% multimap atoms
_passed(presugar,variable_declare(LBL,X,multimap)) :- _passed(defaultArgs,multimap_declare(LBL,X)).
_passed(presugar,multimap_assign(LBL,X,EKEY,EVAL)) :- _passed(defaultArgs,multimap_assign(LBL,X,EKEY,EVAL)).


%%%%%% set atoms
_passed(presugar,variable_declare(LBL,X,set)) :- _passed(defaultArgs,set_declare(LBL,X)).
_passed(presugar,set_assign(LBL,X,E)) :- _passed(defaultArgs,set_assign(LBL,X,E)).
_passed(presugar,set_baseDomain(LBL,X,E)) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)).


%%%%%% optimize atoms
_passed(presugar,optimize_precision(LBL,PREC,PRIO)) :- _passed(defaultArgs,optimize_precision(LBL,PREC,PRIO)).
_passed(presugar,optimize_maximizeSum(LBL,E,X,P)) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)).

%%%%%% preference atoms
_passed(presugar,preference_holds(LBL,operation(eq,(variable(X),(E,()))),K)) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K > 0.
_passed(presugar,preference_holds(LBL,operation(neq,(variable(X),(E,()))),-K)) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K < 0.
_passed(presugar,preference_holds(LBL,E,K)) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K > 0.
_passed(presugar,preference_holds(LBL,operation(wnot,(E,())),-K)) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.
_expression(presugar,operation(wnot,(E,()))) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.


_expression(presugar,operation(eq,(variable(X),(E,())))) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K > 0.
_expression(presugar,operation(neq,(variable(X),(E,())))) :- _passed(defaultArgs,preference_variableValue(LBL,X,E,K)), K < 0.
_expression(presugar,operation(wnot,(E,()))) :- _passed(defaultArgs,preference_holds(LBL,E,K)), K < 0.