_main(wf_check).

%_expression_wellformed(EXPR) :- not _main(wf_check), _expression(presugar,EXPR).
%_expression_wellformed(EXPR) :- not _main(wf_check), _expression(ssa,EXPR).

%%%%%%%%%%%%%%%%% _expression_wellformed
%_expression_query(wf_check,EXPR) :- _main(wf_check), _expression(presugar,EXPR).
%_expression_query(wf_check,EXPR) :- _main(wf_check), _expression(ssa,EXPR).
%_expression_query(wf_check,EXPR) :- _main(wf_check), _statement_introduce(LBL,X,EXPR).
%_expression_wfQuery(EXPR) :- _expression_query(wf_check,EXPR).

_expression_wfQuery(EXPR) :- _main(wf_check), _expression(presugar,EXPR).
_expression_wfQuery(EXPR) :- _main(wf_check), _expression(ssa,EXPR).
_expression_wellformed(bad) :- _main(wf_check).
_expression_wellformed(python(CODE)) :- _expression_wfQuery(python(CODE)), true=@pythonIsString(CODE).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=pythonExtract(PSTMT,PEXPR),true=@pythonIsString(PSTMT),true=@pythonIsString(PEXPR).
_expression_wellformed(val(T,V)) :- _expression_wfQuery(val(T,V)).
_expression_wellformed(variable(X)) :- _expression_wfQuery(variable(X)).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), EXPR=operation(O,L), true=@pythonIsList(L), _expression_wellformed(D) : D=@pythonListElements(L).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), true=@pythonIsTuple(EXPR), _expression_wellformed(D) : D=@pythonTupleElements(EXPR).
_expression_wellformed(lambda(ARGS,E)) :- _expression_wfQuery(lambda(ARGS,E)).
_warning(expression(syntaxError),(),"lambda checks unsupported") :- _expression_wfQuery(lambda(ARGS,E)). %TODO

% TODO: for operations, check that the operator is well-formed


_warning(expression(syntaxError),(),EXPR) :- _expression(defaultArgs,EXPR), not _expression_wellformed(EXPR).
_warning(expression(syntaxError),(),EXPR) :- _expression(ssa,EXPR), not _expression_wellformed(EXPR).








%%%%%%%%%%%%%%%%% check if well-formed
_passed(sugar,bool_evaluate(LBL,E)) :- _passed(presugar,bool_evaluate(LBL,E)), _expression_wellformed(E).
_passed(sugar,ensure(LBL,E)) :- _passed(presugar,ensure(LBL,E)), _expression_wellformed(E).
_passed(sugar,evaluate(LBL,OP,ARGS)) :- _passed(presugar,evaluate(LBL,OP,ARGS)), _expression_wellformed(operation(OP,ARGS)).


%%%%%% variable atoms
_passed(sugar,variable_declare(LBL,X,D)) :- _passed(presugar,variable_declare(LBL,X,D)).
_passed(sugar,variable_domain(LBL,X,E)) :- _passed(presugar,variable_domain(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,variable_domain(LBL,X,bad)) :- _passed(presugar,variable_domain(LBL,X,E)), not _expression_wellformed(E).
%_warning(atom(syntaxError),(),variable_domain(LBL,X,E)) :- _passed(presugar,variable_domain(LBL,X,E)), not _expression_wellformed(E).
_passed(sugar,variable_define(LBL,X,E)) :- _passed(presugar,variable_define(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,variable_define(LBL,X,bad)) :- _passed(presugar,variable_define(LBL,X,E)), not _expression_wellformed(E).
%_warning(atom(syntaxError),(),variable_define(LBL,X,E)) :- _passed(presugar,variable_define(LBL,X,E)), not _expression_wellformed(E). % TODO
_warning(atom(syntaxError),(),DECL) :- _passed(presugar,DECL), not _passed(sugar,DECL).

%%%%%% multimap atoms
_passed(sugar,multimap_assign(LBL,X,K,B)) :- _passed(presugar,multimap_assign(LBL,X,K,B)), _expression_wellformed(K), _expression_wellformed(B).
%_warning(atom(syntaxError),(),multimap_assign(LBL,X,K,B)) :- _passed(presugar,multimap_assign(LBL,X,K,B)),
%    not _passed(sugar,multimap_assign(LBL,X,K,B)).

%%%%% set atoms
_passed(sugar,set_assign(LBL,X,E)) :- _passed(presugar,set_assign(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,set_assign(LBL,X,bad)) :- _passed(presugar,set_assign(LBL,X,E)), not _expression_wellformed(E).
%_warning(atom(syntaxError),(),set_assign(LBL,X,E)) :- _passed(presugar,set_assign(LBL,X,E)), not _expression_wellformed(E).
_passed(sugar,set_baseDomain(LBL,X,E)) :- _passed(presugar,set_baseDomain(LBL,X,E)), _expression_wellformed(E).
_passed(sugar,set_baseDomain(LBL,X,bad)) :- _passed(presugar,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).
%_warning(atom(syntaxError),(),set_baseDomain(LBL,X,E)) :- _passed(presugar,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).

%%%%%% statement atoms
%_atom_ok(execution_declare(LBL,PRG,STMT,INS,OUTS)) :- _passed(presugar,execution_declare(LBL,PRG,STMT,INS,OUTS)),
%    _statement_wellformed(STMT),
%	true=@pythonIsList(INS),
%	true=@pythonIsList(OUTS).
%_atom_ok(execution_run(LBL,PRG)) :- _passed(presugar,execution_run(LBL,PRG)).
_warning(atom(syntaxError),PRG,execution_declare(PRG)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).

%%%%%% optimization atoms
_passed(sugar,optimize_maximizeSum(LBL,E,X,P)) :- _passed(presugar,optimize_maximizeSum(LBL,E,X,P)),
    _expression_wellformed(E),
    (number,_,_,_)=@pythonReify(P).
_passed(sugar,optimize_precision(LBL,PREC,PRIO)) :- _passed(presugar,optimize_precision(LBL,PREC,PRIO)),
    _expression_wellformed(PREC),
    (number,_,_,_)=@pythonReify(PRIO).
%_warning(atom(syntaxError),(),optimize_maximizeSum(LBL,E,X,P)) :- _passed(presugar,optimize_maximizeSum(LBL,E,X,P)),
%    not _passed(sugar,optimize_maximizeSum(LBL,E,X,P)).
%_warning(atom(syntaxError),(),optimize_precision(LBL,PREC,PRIO)) :- _passed(presugar,optimize_precision(LBL,PREC,PRIO)),
%    not _passed(sugar,optimize_precision(LBL,PREC,PRIO)).

%%%%%% preference atoms
_passed(sugar,preference_holds(LBL,E,K)) :- _passed(presugar,preference_holds(LBL,E,K)), _expression_wellformed(E), (number,_,_,_)=@pythonReify(K).

