%%%%%%%%%%%%%%%%% engines
_main_engine(compile;ground;propagator;none).

_main_defaultEngine(ENG) :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngineProvided :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngine(compile) :- not _main_defaultEngineProvided.

_label(LBL) :- _label(LBL,DECL).
_main_requestedEngine(LBL) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- _main_defaultEngine(ENG), not _main_requestedEngine(LBL), _label(LBL).
engine(_internal,compile).
%_passed(propagator,DECL) :- _label(LBL,DECL), engine(LBL,propagator).

%%%%%%%%%%%%%%%%% collect labels
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=bool_evaluate(LBL,E).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=ensure(LBL,E).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=evaluate(LBL,O,ARGS).

%%%%%% variable atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=variable_define(LBL,X,E).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=variable_declare(LBL,X,D).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=variable_domain(LBL,X,E).

%%%%%% multimap atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=multimap_assign(LBL,X,K,B).

%%%%% set atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=set_assign(LBL,X,E).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=set_baseDomain(LBL,X,E).

%%%%%% optimization atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=optimize_maximizeSum(LBL,E,X,PRIO).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=optimize_precision(LBL,PREC,PRIO).

%%%%%% preference atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=preference_holds(LBL,E,K).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=preference_variableValue(LBL,X,E,K).

%%%%%% warning atoms
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=warning_forbid(LBL,KIND).
_label(LBL,DECL) :- _passed(sugar,DECL), DECL=warning_ignore(LBL,KIND).
