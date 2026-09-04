#defined bool_evaluate/1.
#defined bool_evaluate/2.
#defined ensure/1.
#defined ensure/2.
#defined evaluate/2.
#defined evaluate/3.

%%%%%%%%%%%%%%%%% labels are optional
_passed(defaultArgs,_label_anonymous,bool_evaluate(E)) :- bool_evaluate(E).
_passed(defaultArgs,LBL,bool_evaluate(E)) :- bool_evaluate(LBL,E).
_passed(defaultArgs,_label_anonymous,ensure(E)) :- ensure(E).
_passed(defaultArgs,LBL,ensure(E)) :- ensure(LBL,E).
_passed(defaultArgs,_label_anonymous,evaluate(OP,ARGS)) :- evaluate(OP,ARGS).
_passed(defaultArgs,LBL,evaluate(OP,ARGS)) :- evaluate(LBL,OP,ARGS).

%%%%%% variable declare
#defined variable_declare/2.
#defined variable_declare/3.

_defaultArgs_variableDeclared(X) :- variable_declare(X,E).
_defaultArgs_variableDeclared(X) :- variable_declare(LBL,X,E).
_passed(defaultArgs,_label_anonymous,variable_declare(X,E)) :- variable_declare(X,E).
_passed(defaultArgs,LBL,variable_declare(X,D)) :- variable_declare(LBL,X,D).

%%%%%% variable fromFacts
#defined variable_domain/2.
#defined variable_domain/3.

_passed(defaultArgs,_label_anonymous,variable_domain(X,E)) :- variable_domain(X,E), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_domain(X,E)) :- variable_domain(X,E), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,LBL,variable_domain(X,E)) :- variable_domain(LBL,X,E).

%%%%%% variable open
#defined variable_assign/2.
#defined variable_assign/3.
#defined variable_choice/2.
#defined variable_choice/3.
#defined variable_default/2.
#defined variable_default/3.
#defined variable_default/4.
#defined variable_default/5.

_passed(defaultArgs,_label_anonymous,variable_default(X,E,val(bool,true),0)) :- variable_default(X,E), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_default(X,E,val(bool,true),0)) :- variable_default(X,E), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,_label_anonymous,variable_default(X,E,C,0)) :- variable_default(X,E,C), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_default(X,E,C,0)) :- variable_default(X,E,C), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,_label_anonymous,variable_default(X,E,C,P)) :- variable_default(X,E,C,P), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_default(X,E,C,P)) :- variable_default(X,E,C,P), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,LBL,variable_default(X,E,C,P)) :- variable_default(LBL,X,E,C,P).

_passed(defaultArgs,_label_anonymous,variable_assign(X,E)) :- variable_assign(X,E), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_assign(X,E)) :- variable_assign(X,E), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,LBL,variable_assign(X,E)) :- variable_assign(LBL,X,E).

_passed(defaultArgs,_label_anonymous,variable_choice(X,E)) :- variable_choice(X,E), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_choice(X,E)) :- variable_choice(X,E), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,LBL,variable_choice(X,E)) :- variable_choice(LBL,X,E).

%%%%%% variable definition
#defined variable_define/2.
#defined variable_define/3.

_passed(defaultArgs,_label_anonymous,variable_define(X,E)) :- variable_define(X,E), not _defaultArgs_variableDeclared(X).
_passed(defaultArgs,LBL,variable_define(X,E)) :- variable_define(X,E), _passed(defaultArgs,LBL,variable_declare(X,D)).
_passed(defaultArgs,LBL,variable_define(X,E)) :- variable_define(LBL,X,E).

%%%%%% multimap atoms
#defined multimap_assign/3.
#defined multimap_assign/4.

_passed(defaultArgs,_label_anonymous,multimap_assign(X,EKEY,EVAL)) :- multimap_assign(X,EKEY,EVAL).
_passed(defaultArgs,LBL,multimap_assign(X,EKEY,EVAL)) :- multimap_assign(LBL,X,EKEY,EVAL).

%%%%% set atoms
#defined set_assign/2.
#defined set_assign/3.
#defined set_baseDomain/2.
#defined set_baseDomain/3.

_passed(defaultArgs,_label_anonymous,set_assign(X,E)) :- set_assign(X,E).
_passed(defaultArgs,LBL,set_assign(X,E)) :- set_assign(LBL,X,E).
_passed(defaultArgs,_label_anonymous,set_baseDomain(X,V)) :- set_baseDomain(X,V).
_passed(defaultArgs,LBL,set_baseDomain(X,V)) :- set_baseDomain(LBL,X,V).

%%%%%% statement atoms
#defined execution_declare/4.
#defined execution_declare/5.
#defined execution_run/1.
#defined execution_run/2.

_passed(defaultArgs,NAME,execution_declare(NAME,STMT,INS,OUTS)) :- execution_declare(NAME,STMT,INS,OUTS).
_passed(defaultArgs,LBL,execution_declare(NAME,STMT,INS,OUTS)) :- execution_declare(LBL,NAME,STMT,INS,OUTS).
_passed(defaultArgs,NAME,execution_run(NAME)) :- execution_run(NAME), _passed(defaultArgs,LBL,execution_declare(NAME,STMT,INS,OUTS)).
_passed(defaultArgs,LBL,execution_run(NAME)) :- execution_run(LBL,NAME).

%%%%%% optimization atoms
#defined optimize_precision/1.
#defined optimize_precision/2.
#defined optimize_maximizeSum/2.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.

_passed(defaultArgs,_label_anonymous,optimize_maximizeSum(E,X,0)) :- optimize_maximizeSum(E,X).
_passed(defaultArgs,_label_anonymous,optimize_maximizeSum(E,X,P)) :- optimize_maximizeSum(E,X,P).
_passed(defaultArgs,LBL,optimize_maximizeSum(E,X,P)) :- optimize_maximizeSum(LBL,E,X,P).

% 4-parameter version with explicit priority
% Precision for specific priority (priority is last argument)
_passed(defaultArgs,_label_anonymous,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC,PRIO).
% Default precision for all priorities if not specified
_defaultArgs_optimizePrecision(PREC) :- optimize_precision(PREC).
_defaultArgs_precisionProj :- optimize_precision(PREC).
_defaultArgs_precisionProj(PRIO) :- optimize_precision(PREC,PRIO).
% Default precision value of 1 if no precision is specified at all
_defaultArgs_optimizePrecision(val(int,1)) :- not _defaultArgs_precisionProj.
_defaultArgs_optimize_priority(PRIO) :- _passed(defaultArgs,LBL,optimize_maximizeSum(E,X,PRIO)).
_passed(defaultArgs,_label_anonymous,optimize_precision(PREC,PRIO)) :- _defaultArgs_optimizePrecision(PREC), _defaultArgs_optimize_priority(PRIO), not _defaultArgs_precisionProj(PRIO).

%%%%%% preference atoms
#defined preference_holds/3.
#defined preference_holds/2.
#defined preference_holds/1.
#defined preference_variableValue/4.
#defined preference_variableValue/3.
#defined preference_variableValue/2.
_passed(defaultArgs,_label_anonymous,preference_holds(E,1)) :- preference_holds(E).
_passed(defaultArgs,_label_anonymous,preference_holds(E,K)) :- preference_holds(E,K).
_passed(defaultArgs,LBL,preference_holds(E,K)) :- preference_holds(LBL,E,K).
_passed(defaultArgs,_label_anonymous,preference_variableValue(X,E,1)) :- preference_variableValue(X,E).
_passed(defaultArgs,_label_anonymous,preference_variableValue(X,E,K)) :- preference_variableValue(X,E,K).
_passed(defaultArgs,LBL,preference_variableValue(X,E,K)) :- preference_variableValue(LBL,X,E,K).

%%%%%% warning atoms
#defined warning_forbid/1.
#defined warning_forbid/2.
#defined warning_ignore/1.
#defined warning_ignore/2.

_passed(defaultArgs,_label_anonymous,warning_forbid(KIND,_internal(all))) :- warning_forbid(KIND).
_passed(defaultArgs,_label_anonymous,warning_forbid(KIND,LBL)) :- warning_forbid(KIND,LBL).
_passed(defaultArgs,_label_anonymous,warning_ignore(KIND,_internal(all))) :- warning_ignore(KIND).
_passed(defaultArgs,_label_anonymous,warning_ignore(KIND,LBL)) :- warning_ignore(KIND,LBL).
