%%%%%%%%%%%%%%%%% semantic expression atoms
_passed(sugar,LBL,bool_evaluate(E)) :- _passed(defaultArgs,LBL,bool_evaluate(E)).

_passed(sugar,LBL,check(E)) :- _passed(defaultArgs,LBL,check(E)).

_passed(sugar,LBL,ensure(E)) :- _passed(defaultArgs,LBL,ensure(E)).

_passed(sugar,LBL,evaluate(E,E)) :- _passed(defaultArgs,LBL,evaluate(E)).
_passed(sugar,LBL,warning_raise(KIND,MSG,COND)) :- _passed(defaultArgs,LBL,warning_raise(KIND,MSG,COND)).

%%%%%% variable fromFacts atoms
_passed(sugar,LBL,variable_declare(X,D,C)) :- _passed(defaultArgs,LBL,variable_declare(X,D,C)), D=(definition;fromFacts;open;set;multimap).
_passed(sugar,LBL,variable_declare(X,fromFacts,C)) :- _passed(defaultArgs,LBL,variable_declare(X,boolDomain,C)).
_passed(sugar,LBL,variable_domain(X,val(bool,(false;true)),C)) :- _passed(defaultArgs,LBL,variable_declare(X,boolDomain,C)).

%%%%%% variable define
_passed(sugar,LBL,variable_declare(X,definition,val(bool,true))) :- _passed(defaultArgs,LBL,variable_define(X,E,C)), not _defaultArgs_variableDeclared(X).
_passed(sugar,LBL,variable_define(X,E,C)) :- _passed(defaultArgs,LBL,variable_define(X,E,C)).

%%%%%% variable domain
_passed(sugar,LBL,variable_domain(X,E,C)) :- _passed(defaultArgs,LBL,variable_domain(X,E,C)).

%%%%%% variable assign
_passed(sugar,LBL,variable_assign(X,E,C)) :- _passed(defaultArgs,LBL,variable_assign(X,E,C)).

%%%%%% variable choice
_passed(sugar,LBL,variable_choice(X,E,C)) :- _passed(defaultArgs,LBL,variable_choice(X,E,C)).

%%%%%% variable default
_passed(sugar,LBL,variable_default(X,D,C,P)) :- _passed(defaultArgs,LBL,variable_default(X,D,C,P)).


%%%%%% multimap atoms
_passed(sugar,LBL,multimap_assign(X,EKEY,EVAL,C)) :- _passed(defaultArgs,LBL,multimap_assign(X,EKEY,EVAL,C)).


%%%%%% set atoms
_passed(sugar,LBL,set_assign(X,E,C)) :- _passed(defaultArgs,LBL,set_assign(X,E,C)).
_passed(sugar,LBL,set_baseDomain(X,E,C)) :- _passed(defaultArgs,LBL,set_baseDomain(X,E,C)).

%%%%%% optimize atoms
_sugar_aux(LBL,optimize_component(EXPR,E,PREC,ID,PRIO,C)) :-
  _passed(defaultArgs,LBL,optimize_maximizeSum(E,ID,PRIO,C)),
  _passed(defaultArgs,LBL2,optimize_precision(PREC,PRIO)),
  EXPR=operation(floor,(operation(mult,(E,(PREC,()))),())).

_passed(sugar,LBL,optimize_component(E,O,P,ID,PRIORITY,C)) :- _sugar_aux(LBL,optimize_component(E,O,P,ID,PRIORITY,C)).

%%%%%% preference atoms
_sugar_aux(LBL,preference_holds(operation(eq,(variable(X),(E,()))),K,C)) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K,C)), K > 0.
_sugar_aux(LBL,preference_holds(operation(neq,(variable(X),(E,()))),-K,C)) :- _passed(defaultArgs,LBL,preference_variableValue(X,E,K,C)), K < 0.
_sugar_aux(LBL,preference_holds(E,K,C)) :- _passed(defaultArgs,LBL,preference_holds(E,K,C)), K > 0.
_sugar_aux(LBL,preference_holds(operation(wnot,(E,())),-K,C)) :- _passed(defaultArgs,LBL,preference_holds(E,K,C)), K < 0.

_passed(sugar,LBL,preference_holds(K,E)) :- _sugar_aux(LBL,preference_holds(E,K,E)).
_passed(sugar,LBL,preference_holds(K,E)) :- _sugar_aux(LBL,preference_holds(E,K,val(bool,true))), E != val(bool,true).
_passed(sugar,LBL,preference_holds(K,C)) :- _sugar_aux(LBL,preference_holds(val(bool,true),K,C)), C != val(bool,true).
_passed(sugar,LBL,preference_holds(K,val(bool,false))) :- _sugar_aux(LBL,preference_holds(val(bool,false),K,C)).
_passed(sugar,LBL,preference_holds(K,val(bool,false))) :- _sugar_aux(LBL,preference_holds(E,K,val(bool,false))).
_passed(sugar,LBL,preference_holds(K,operation(conj,(C,(E,()))))) :- _sugar_aux(LBL,preference_holds(E,K,C)), E != C, E != val(bool,true), C != val(bool,true), E != val(bool,false), C != val(bool,false).

%%%%%% ssa atoms
_passed(sugar,LBL,DEC) :- _passed(ssa,LBL,DEC).
_variable(sugar,X) :- _variable(ssa,X).

%%%%%% internal declarations
_passed(internal_declaration,LBL,variable_declare(X,DOM,C)) :- _passed(ssa,LBL,variable_declare(X,DOM,C)), _execution_outputVar(LBL,PRG,N,X).
_passed(internal_declaration,LBL,variable_define(X,DEF,COND)) :- _passed(ssa,LBL,variable_define(X,DEF,COND)), _execution_outputVar(LBL,PRG,N,X).
_passed(internal_declaration,LBL,check(E)) :- _passed(ssa,LBL,check(E)).
