#defined bool_evaluate/1.
#defined bool_evaluate/2.
#defined ensure/1.
#defined ensure/2.
#defined evaluate/2.
#defined evaluate/3.

%%%%%%%%%%%%%%%%% labels are optional
_passed(defaultArgs,bool_evaluate(_label_anonymous,E)) :- bool_evaluate(E).
_passed(defaultArgs,bool_evaluate(LBL,E)) :- bool_evaluate(LBL,E).
_passed(defaultArgs,ensure(_label_anonymous,E)) :- ensure(E).
_passed(defaultArgs,ensure(LBL,E)) :- ensure(LBL,E).
_passed(defaultArgs,evaluate(_label_anonymous,OP,ARGS)) :- evaluate(OP,ARGS).
_passed(defaultArgs,evaluate(LBL,OP,ARGS)) :- evaluate(LBL,OP,ARGS).

%%%%%% variable atoms
#defined variable_declare/2.
#defined variable_declare/3.
#defined variable_declareOptional/1.
#defined variable_declareOptional/2.
#defined variable_define/2.
#defined variable_define/3.
#defined variable_domain/2.
#defined variable_domain/3.

_passed(defaultArgs,variable_declare(_label_anonymous,X,E)) :- variable_declare(X,E).
_passed(defaultArgs,variable_declare(LBL,X,D)) :- variable_declare(LBL,X,D).
_passed(defaultArgs,variable_declareOptional(_label_anonymous,X)) :- variable_declareOptional(X), not _passed(defaultArgs,variable_declare(_,X,_)).
_passed(defaultArgs,variable_declareOptional(LBL,X)) :- variable_declareOptional(X), _passed(defaultArgs,variable_declare(LBL,X,D)).
_passed(defaultArgs,variable_declareOptional(LBL,X)) :- variable_declareOptional(LBL,X).
_passed(defaultArgs,variable_define(_label_anonymous,X,E)) :- variable_define(X,E).
_passed(defaultArgs,variable_define(LBL,X,E)) :- variable_define(LBL,X,E).
_passed(defaultArgs,variable_domain(_label_anonymous,X,E)) :- variable_domain(X,E), not _passed(defaultArgs,variable_declare(_,X,_)).
_passed(defaultArgs,variable_domain(LBL,X,E)) :- variable_domain(X,E), _passed(defaultArgs,variable_declare(LBL,X,D)).
_passed(defaultArgs,variable_domain(LBL,X,E)) :- variable_domain(LBL,X,E).

%%%%%% multimap atoms
#defined multimap_declare/1.
#defined multimap_declare/2.
#defined multimap_assign/3.
#defined multimap_assign/4.

_passed(defaultArgs,multimap_declare(_label_anonymous,X)) :- multimap_declare(X).
_passed(defaultArgs,multimap_declare(LBL,X)) :- multimap_declare(LBL,X).
_passed(defaultArgs,multimap_assign(_label_anonymous,X,EKEY,EVAL)) :- multimap_assign(X,EKEY,EVAL).
_passed(defaultArgs,multimap_assign(LBL,X,EKEY,EVAL)) :- multimap_assign(LBL,X,EKEY,EVAL).

%%%%% set atoms
#defined set_declare/1.
#defined set_declare/2.
#defined set_assign/2.
#defined set_assign/3.
#defined set_baseDomain/2.
#defined set_baseDomain/3.

_passed(defaultArgs,set_declare(_label_anonymous,X)) :- set_declare(X).
_passed(defaultArgs,set_declare(LBL,X)) :- set_declare(LBL,X).
_passed(defaultArgs,set_assign(_label_anonymous,X,E)) :- set_assign(X,E).
_passed(defaultArgs,set_assign(LBL,X,E)) :- set_assign(LBL,X,E).
_passed(defaultArgs,set_baseDomain(_label_anonymous,X,V)) :- set_baseDomain(X,V).
_passed(defaultArgs,set_baseDomain(LBL,X,V)) :- set_baseDomain(LBL,X,V).

%%%%%% statement atoms
#defined execution_declare/4.
#defined execution_declare/5.
#defined execution_run/1.
#defined execution_run/2.

_passed(defaultArgs,execution_declare(_label_anonymous,NAME,STMT,INS,OUTS)) :- execution_declare(NAME,STMT,INS,OUTS).
_passed(defaultArgs,execution_declare(LBL,NAME,STMT,INS,OUTS)) :- execution_declare(LBL,NAME,STMT,INS,OUTS).
_passed(defaultArgs,execution_run(_label_anonymous,NAME)) :- execution_run(NAME).
_passed(defaultArgs,execution_run(LBL,NAME)) :- execution_run(LBL,NAME).

%%%%%% optimization atoms
#defined optimize_precision/1.
#defined optimize_precision/2.
#defined optimize_maximizeSum/2.
#defined optimize_maximizeSum/3.
#defined optimize_maximizeSum/4.

_passed(defaultArgs,optimize_maximizeSum(_label_anonymous,E,X,0)) :- optimize_maximizeSum(E,X).
_passed(defaultArgs,optimize_maximizeSum(_label_anonymous,E,X,P)) :- optimize_maximizeSum(E,X,P).
_passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)) :- optimize_maximizeSum(LBL,E,X,P).

% 4-parameter version with explicit priority
% Precision for specific priority (priority is last argument)
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- optimize_precision(PREC,PRIO).
% Default precision for all priorities if not specified
_passed(defaultArgs,optimize_precision(PREC)) :- optimize_precision(PREC).
% Default precision value of 1 if no precision is specified at all
_passed(defaultArgs,optimize_precision(val(int,1))) :- not optimize_precision(_).
_optimize_priority(PRIO) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,PRIO)).
_passed(defaultArgs,optimize_precision(PREC,PRIO)) :- _passed(defaultArgs,optimize_precision(PREC)), _optimize_priority(PRIO), not optimize_precision(_,PRIO).

%%%%%% preference atoms
#defined preference_holds/3.
#defined preference_holds/2.
#defined preference_holds/1.
#defined preference_variableValue/4.
#defined preference_variableValue/3.
#defined preference_variableValue/2.
_passed(defaultArgs,preference_holds(_label_anonymous,E,1)) :- preference_holds(E).
_passed(defaultArgs,preference_holds(_label_anonymous,E,K)) :- preference_holds(E,K).
_passed(defaultArgs,preference_holds(LBL,E,K)) :- preference_holds(LBL,E,K).
_passed(defaultArgs,preference_variableValue(_label_anonymous,X,E,1)) :- preference_variableValue(X,E).
_passed(defaultArgs,preference_variableValue(_label_anonymous,X,E,K)) :- preference_variableValue(X,E,K).
_passed(defaultArgs,preference_variableValue(LBL,X,E,K)) :- preference_variableValue(LBL,X,E,K).

%%%%%% warning atoms
#defined warning_forbid/1.
#defined warning_ignore/1.

_passed(defaultArgs,warning_forbid(_label_anonymous,KIND)) :- warning_forbid(KIND).
_passed(defaultArgs,warning_forbid(LBL,KIND)) :- warning_forbid(LBL,KIND).
_passed(defaultArgs,warning_ignore(_label_anonymous,KIND)) :- warning_ignore(KIND).
_passed(defaultArgs,warning_ignore(LBL,KIND)) :- warning_ignore(LBL,KIND).

%%%%%%%%%%%%%%%%% collect labels
_label(LBL) :- _passed(defaultArgs,bool_evaluate(LBL,E)).
_label(LBL) :- _passed(defaultArgs,ensure(LBL,E)).
_label(LBL) :- _passed(defaultArgs,evaluate(LBL,O,ARGS)).

%%%%%% variable atoms
_label(LBL) :- _passed(defaultArgs,variable_define(LBL,X,E)).
_label(LBL) :- _passed(defaultArgs,variable_declare(LBL,X,D)).
_label(LBL) :- _passed(defaultArgs,variable_domain(LBL,X,E)).

%%%%%% multimap atoms
_label(LBL) :- _passed(defaultArgs,multimap_declare(LBL,X)).
_label(LBL) :- _passed(defaultArgs,multimap_assign(LBL,X,K,B)).

%%%%% set atoms
_label(LBL) :- _passed(defaultArgs,set_declare(LBL,X)).
_label(LBL) :- _passed(defaultArgs,set_assign(LBL,X,E)).
_label(LBL) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)).

%%%%%% statement atoms
_label(LBL) :- _passed(defaultArgs,execution_declare(LBL,NAME,STMT,INS,OUTS)).
_label(LBL) :- _passed(defaultArgs,execution_run(LBL,NAME)).

%%%%%% optimization atoms
_label(LBL) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,PRIO)).

%%%%%% preference atoms
_label(LABEL) :- _passed(defaultArgs,preference_holds(LABEL,E,K)).
_label(LABEL) :- _passed(defaultArgs,preference_variableValue(LABEL,X,E,K)).

%%%%%% warning atoms
_label(LABEL) :- _passed(defaultArgs,warning_forbid(LABEL,KIND)).
_label(LABEL) :- _passed(defaultArgs,warning_ignore(LABEL,KIND)).
