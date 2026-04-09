#defined assign/2.
#defined define/3.
#defined ensure/1.
#defined evaluate/2.

%%%%%%%%%%%%%%%%% labels are optional
ensure(_label_anonymous,E) :- ensure(E).
assign(_label_anonymous,X,E) :- assign(X,E).
define(_label_anonymous,X,VARS,EXPR) :- define(X,VARS,EXPR).

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



%%%%%%%%%%%%%%%%% check if well-formed