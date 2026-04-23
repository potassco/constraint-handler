#defined assign/2.
#defined assign/3.
#defined ensure/1.
#defined ensure/2.
#defined evaluate/2.
#defined evaluate/3.

variable_define(X,E) :- assign(X,E).
variable_define(LBL,X,E) :- assign(LBL,X,E).

%%%%%%%%%%%%%%%%% labels are optional
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

warning_forbid(_label_anonymous,KIND) :- warning_forbid(KIND).
warning_ignore(_label_anonymous,KIND) :- warning_ignore(KIND).

%%%%%%%%%%%%%%%%% collect labels
_label(LABEL) :- _passed(defaultArgs,ensure(LABEL,E)).
_label(LABEL) :- _passed(defaultArgs,evaluate(LABEL,O,ARGS)).

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
_label(LABEL) :- warning_forbid(LABEL,KIND).
_label(LABEL) :- warning_ignore(LABEL,KIND).



%%%%%%%%%%%%%%%%% check if well-formed
_passed(sugar,ensure(LBL,E)) :- _passed(defaultArgs,ensure(LBL,E)), _expression_wellformed(E).
_passed(sugar,evaluate(LBL,OP,ARGS)) :- _passed(defaultArgs,evaluate(LBL,OP,ARGS)), _expression_wellformed(operation(OP,ARGS)).


%%%%%% multimap atoms
_passed(sugar,multimap_declare(LBL,X)) :- _passed(defaultArgs,multimap_declare(LBL,X)).
_passed(sugar,multimap_assign(LBL,X,K,B)) :- _passed(defaultArgs,multimap_assign(LBL,X,K,B)), _expression_wellformed(K), _expression_wellformed(B).
_warning(atom(syntaxError),(),multimap_assign(LBL,X,K,B)) :- _passed(defaultArgs,multimap_assign(LBL,X,K,B)),
    not _passed(sugar,multimap_assign(LBL,X,K,B)).

%%%%% set atoms
_passed(sugar,set_declare(LBL,X)) :- _passed(defaultArgs,set_declare(LBL,X)).
_passed(sugar,set_assign(LBL,X,E)) :- _passed(defaultArgs,set_assign(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,set_assign(LBL,X,bad)) :- _passed(defaultArgs,set_assign(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),set_assign(LBL,X,E)) :- _passed(defaultArgs,set_assign(LBL,X,E)), not _expression_wellformed(E).
_passed(sugar,set_baseDomain(LBL,X,E)) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,set_baseDomain(LBL,X,bad)) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),set_baseDomain(LBL,X,E)) :- _passed(defaultArgs,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).

%%%%%% statement atoms
_passed(sugar,execution_declare(LBL,PRG,STMT,INS,OUTS)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
    _statement_wellformed(STMT),
	true=@pythonIsList(INS),
	true=@pythonIsList(OUTS).
_passed(sugar,execution_run(LBL,PRG)) :- _passed(defaultArgs,execution_run(LBL,PRG)).
_warning(atom(syntaxError),(PRG,()),execution_declare(PRG)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).

%%%%%% optimization atoms
_passed(sugar,optimize_maximizeSum(LBL,E,X,P)) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)),
    _expression_wellformed(E),
    (number,_,_,_)=@pythonReify(P).
_passed(sugar,optimize_precision(PREC,PRIO)) :- _passed(defaultArgs,optimize_precision(PREC,PRIO)),
    _expression_wellformed(PREC),
    (number,_,_,_)=@pythonReify(PRIO).
_warning(atom(syntaxError),(),optimize_maximizeSum(LBL,E,X,P)) :- _passed(defaultArgs,optimize_maximizeSum(LBL,E,X,P)),
    not _passed(sugar,optimize_maximizeSum(LBL,E,X,P)).
_warning(atom(syntaxError),(),optimize_precision(PREC,PRIO)) :- _passed(defaultArgs,optimize_precision(PREC,PRIO)),
    not _passed(sugar,optimize_precision(PREC,PRIO)).

%%%%%% preference atoms
_passed(sugar,preference_holds(LABEL,E,K)) :- _passed(defaultArgs,preference_holds(LABEL,E,K)), _expression_wellformed(E), (number,_,_,_)=@pythonReify(K).
_passed(sugar,preference_variableValue(LABEL,X,E,K)) :- _passed(defaultArgs,preference_variableValue(LABEL,X,E,K)), _expression_wellformed(E), (number,_,_,_)=@pythonReify(K).
_passed(sugar,preference_expressionScore(LBL,operation(eq,(variable(X),(E,()))),K)) :- _passed(sugar,preference_variableValue(LBL,X,E,K)), K > 0.
_passed(sugar,preference_expressionScore(LBL,operation(neq,(variable(X),(E,()))),-K)) :- _passed(sugar,preference_variableValue(LBL,X,E,K)), K < 0.
_passed(sugar,preference_expressionScore(LBL,E,K)) :- _passed(sugar,preference_holds(LBL,E,K)), K > 0.
_passed(sugar,preference_expressionScore(LBL,operation(wnot,(E,())),-K)) :- _passed(sugar,preference_holds(LBL,E,K)), K < 0.

%%%%%% warning atoms
