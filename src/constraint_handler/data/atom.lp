#defined assign/2.
#defined define/3.
#defined ensure/1.
#defined evaluate/2.

%%%%%%%%%%%%%%%%% labels are optional
ensure(_label_anonymous,E) :- ensure(E).
assign(_label_anonymous,X,E) :- assign(X,E).
define(_label_anonymous,X,VARS,EXPR) :- define(X,VARS,EXPR).
evaluate(_label_anonymous,OP,ARGS) :- evaluate(OP,ARGS).

%%%%%% variable atoms
#defined variable_declare/2.
#defined variable_declareOptional/1.
#defined variable_define/2.
#defined variable_domain/2.

variable_define(_label_anonymous,X,E) :- variable_define(X,E).
variable_declare(_label_anonymous,X,E) :- variable_declare(X,E).

%%%%%% multimap atoms
#defined multimap_declare/1.
#defined multimap_assign/3.

multimap_declare(_label_anonymous,X) :- multimap_declare(X).
multimap_assign(_label_anonymous,X,EKEY,EVAL) :- multimap_assign(X,EKEY,EVAL).

%%%%% set atoms
#defined set_declare/1.
#defined set_assign/2.
#defined set_baseDomain/2.

set_declare(_label_anonymous,X) :- set_declare(X).
set_assign(_label_anonymous,X,E) :- set_assign(X,E).
set_baseDomain(_label_anonymous,X,V) :- set_baseDomain(X,V).

%%%%%% statement atoms
#defined execution_declare/4.
#defined execution_run/1.

execution_declare(_label_anonymous,NAME,STMT,INS,OUTS) :- execution_declare(NAME,STMT,INS,OUTS).
execution_run(_label_anonymous,NAME) :- execution_run(NAME).

%%%%%% optimization atoms
#defined optimize_precision/1.
#defined optimize_precision/2.
#defined optimize_maximizeSum/2.
#defined optimize_maximizeSum/3.

optimize_maximizeSum(_label_anonymous,E,X,P) :- optimize_maximizeSum(E,X,P).
optimize_maximizeSum(_label_anonymous,E,X,0) :- optimize_maximizeSum(E,X).

%%%%%% preference atoms
#defined preference_holds/2.
#defined preference_holds/1.
#defined preference_variableValue/3.
#defined preference_variableValue/2.
preference_holds(_label_anonymous,E,K) :- preference_holds(E,K).
preference_variableValue(_label_anonymous,X,E,K) :- preference_variableValue(X,E,K).
%%% convenience
preference_holds(_label_anonymous,E,1) :- preference_holds(E).
preference_variableValue(_label_anonymous,X,E,1) :- preference_variableValue(X,E).

%%%%%% warning atoms
#defined forbid_warning/1.
#defined ignore_warning/1.

forbid_warning(_label_anonymous,KIND) :- forbid_warning(KIND).


%%%%%%%%%%%%%%%%% collect labels
_label(LABEL) :- ensure(LABEL,_).
_label(LABEL) :- assign(LABEL,_,_).
_label(LABEL) :- define(LABEL,_,_,_).
_label(LABEL) :- evaluate(LABEL,_,_).

%%%%%% variable atoms
_label(LABEL) :- variable_define(LABEL,_,_).
_label(LABEL) :- variable_declare(LABEL,_,_).

%%%%%% multimap atoms
_label(LABEL) :- multimap_declare(LABEL,_).
_label(LABEL) :- multimap_assign(LABEL,_,_,_).

%%%%% set atoms
_label(LABEL) :- set_declare(LABEL,_).
_label(LABEL) :- set_assign(LABEL,_,_).
_label(LABEL) :- set_baseDomain(LABEL,_,_).

%%%%%% statement atoms
_label(LABEL) :- execution_declare(LABEL,_,_,_,_).
_label(LABEL) :- execution_run(LABEL,_).

%%%%%% optimization atoms
_label(LABEL) :- optimize_maximizeSum(LABEL,_,_,_).

%%%%%% preference atoms
_label(LABEL) :- preference_holds(LABEL,_,_).
_label(LABEL) :- preference_variableValue(LABEL,_,_,_).

%%%%%% warning atoms
_label(LABEL) :- forbid_warning(LABEL,_).



%%%%%%%%%%%%%%%%% check if well-formed