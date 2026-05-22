%%%%%%%%%%%%%%%%% check if well-formed
_passed(wf_check,ensure(LBL,E)) :- _passed(sugar,ensure(LBL,E)), _expression_wellformed(E).
_passed(wf_check,evaluate(LBL,OP,ARGS)) :- _passed(sugar,evaluate(LBL,OP,ARGS)), _expression_wellformed(operation(OP,ARGS)).


%%%%%% variable atoms
_passed(wf_check,variable_declare(LBL,X,D)) :- _passed(sugar,variable_declare(LBL,X,D)).
_passed(wf_check,variable_domain(LBL,X,E)) :- _passed(sugar,variable_domain(LBL,X,E)), _expression_wellformed(E).
_passed(wf_check,variable_domain(LBL,X,bad)) :- _passed(sugar,variable_domain(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),variable_domain(LBL,X,E)) :- _passed(sugar,variable_domain(LBL,X,E)), not _expression_wellformed(E).
_passed(wf_check,variable_define(LBL,X,E)) :- _passed(sugar,variable_define(LBL,X,E)), _expression_wellformed(E).
_passed(wf_check,variable_define(LBL,X,bad)) :- _passed(sugar,variable_define(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),variable_define(LBL,X,E)) :- _passed(sugar,variable_define(LBL,X,E)), not _expression_wellformed(E). % TODO


%%%%%% multimap atoms
_passed(wf_check,multimap_declare(LBL,X)) :- _passed(sugar,multimap_declare(LBL,X)).
_passed(wf_check,multimap_assign(LBL,X,K,B)) :- _passed(sugar,multimap_assign(LBL,X,K,B)), _expression_wellformed(K), _expression_wellformed(B).
_warning(atom(syntaxError),(),multimap_assign(LBL,X,K,B)) :- _passed(sugar,multimap_assign(LBL,X,K,B)),
    not _passed(wf_check,multimap_assign(LBL,X,K,B)).

%%%%% set atoms
_passed(wf_check,set_declare(LBL,X)) :- _passed(sugar,set_declare(LBL,X)).
_passed(wf_check,set_assign(LBL,X,E)) :- _passed(sugar,set_assign(LBL,X,E)), _expression_wellformed(E).
_passed(wf_check,set_assign(LBL,X,bad)) :- _passed(sugar,set_assign(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),set_assign(LBL,X,E)) :- _passed(sugar,set_assign(LBL,X,E)), not _expression_wellformed(E).
_passed(wf_check,set_baseDomain(LBL,X,E)) :- _passed(sugar,set_baseDomain(LBL,X,E)), _expression_wellformed(E).
_passed(wf_check,set_baseDomain(LBL,X,bad)) :- _passed(sugar,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),set_baseDomain(LBL,X,E)) :- _passed(sugar,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).

%%%%%% statement atoms
%_atom_ok(execution_declare(LBL,PRG,STMT,INS,OUTS)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
%    _statement_wellformed(STMT),
%	true=@pythonIsList(INS),
%	true=@pythonIsList(OUTS).
%_atom_ok(execution_run(LBL,PRG)) :- _passed(defaultArgs,execution_run(LBL,PRG)).
_warning(atom(syntaxError),PRG,execution_declare(PRG)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).

%%%%%% optimization atoms
_passed(wf_check,optimize_maximizeSum(LBL,E,X,P)) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)),
    _expression_wellformed(E),
    (number,_,_,_)=@pythonReify(P).
_passed(wf_check,optimize_precision(PREC,PRIO)) :- _passed(sugar,optimize_precision(PREC,PRIO)),
    _expression_wellformed(PREC),
    (number,_,_,_)=@pythonReify(PRIO).
_warning(atom(syntaxError),(),optimize_maximizeSum(LBL,E,X,P)) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)),
    not _passed(wf_check,optimize_maximizeSum(LBL,E,X,P)).
_warning(atom(syntaxError),(),optimize_precision(PREC,PRIO)) :- _passed(sugar,optimize_precision(PREC,PRIO)),
    not _passed(wf_check,optimize_precision(PREC,PRIO)).

%%%%%% preference atoms
_passed(wf_check,preference_holds(LBL,E,K)) :- _passed(sugar,preference_holds(LBL,E,K)), _expression_wellformed(E), (number,_,_,_)=@pythonReify(K).


%%%%%% warning atoms
