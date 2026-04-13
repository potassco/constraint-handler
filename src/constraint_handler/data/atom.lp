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

variable_declare(_label_anonymous,X,E) :- variable_declare(X,E).
variable_declareOptional(LABEL,X) :- variable_declareOptional(X), variable_declare(LABEL,X,_).
variable_declareOptional(_label_anonymous,X) :- variable_declareOptional(X), not variable_declare(_,X,_).
variable_define(_label_anonymous,X,E) :- variable_define(X,E).
variable_domain(LABEL,X,E) :- variable_domain(X,E), variable_declare(LABEL,X,_).
variable_domain(_label_anonymous,X,E) :- variable_domain(X,E), not variable_declare(_,X,_).

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
_label(LABEL) :- ensure(LABEL,E).
_label(LABEL) :- assign(LABEL,X,E).
_label(LABEL) :- define(LABEL,_,_,_).
_label(LABEL) :- evaluate(LABEL,O,ARGS).

%%%%%% variable atoms
_label(LABEL) :- variable_define(LABEL,X,E).
_label(LABEL) :- variable_declare(LABEL,X,D).
_label(LABEL) :- variable_domain(LABEL,X,E).

%%%%%% multimap atoms
_label(LABEL) :- multimap_declare(LABEL,X).
_label(LABEL) :- multimap_assign(LABEL,X,K,B).

%%%%% set atoms
_label(LABEL) :- set_declare(LABEL,X).
_label(LABEL) :- set_assign(LABEL,X,E).
_label(LABEL) :- set_baseDomain(LABEL,X,E).

%%%%%% statement atoms
_label(LABEL) :- execution_declare(LABEL,NAME,STMT,INS,OUTS).
_label(LABEL) :- execution_run(LABEL,NAME).

%%%%%% optimization atoms
_label(LABEL) :- optimize_maximizeSum(LABEL,_,_,_).

%%%%%% preference atoms
_label(LABEL) :- preference_holds(LABEL,_,_).
_label(LABEL) :- preference_variableValue(LABEL,_,_,_).

%%%%%% warning atoms
_label(LABEL) :- forbid_warning(LABEL,KIND).



%%%%%%%%%%%%%%%%% check if well-formed
_passed(sugar,ensure(LABEL,E)) :- ensure(LABEL,E), _expression_wellformed(E).
_passed(sugar,evaluate(LABEL,OP,ARGS)) :- evaluate(LABEL,OP,ARGS), _expression_wellformed(operation(OP,ARGS)).


_label(LABEL) :- define(LABEL,_,_,_).
%_passed(sugar,assign(LABEL,X,E)) :- assign(LABEL,X,E), _expression_wellformed(E).


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
