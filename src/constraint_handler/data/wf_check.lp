_main(wf_check).

%%%%%%%%%%%%%%%%% _expression_wellformed
_expression_wfQuery(EXPR) :- _main(wf_check), _expression(sugar,EXPR).
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


_warning(expression(syntaxError),(),EXPR) :- _main(wf_check), _expression(sugar,EXPR), not _expression_wellformed(EXPR).








%%%%%%%%%%%%%%%%% check if well-formed


%%%%%% variable atoms
_passed(correction(wf),variable_domain(LBL,X,E),variable_domain(LBL,X,bad)) :- _passed(sugar,variable_domain(LBL,X,E)), not _expression_wellformed(E).
_passed(correction(wf),variable_define(LBL,X,E),variable_define(LBL,X,bad)) :- _passed(sugar,variable_define(LBL,X,E)), not _expression_wellformed(E).
_warning(atom(syntaxError),(),DECL) :- _passed(correction(wf),DECL,NDECL).

%%%%%% multimap atoms
%_passed(correction(wf),multimap_assign(LBL,X,K,B),multimap_assign(LBL,X,bad,bad)) :- _passed(sugar,multimap_assign(LBL,X,K,B)), #false : _expression_wellformed(K), _expression_wellformed(B).
%%%% TODO

%%%%% set atoms
_passed(correction(wf),set_assign(LBL,X,E),set_assign(LBL,X,bad)) :- _passed(sugar,set_assign(LBL,X,E)), not _expression_wellformed(E).
_passed(correction(wf),set_baseDomain(LBL,X,E),set_baseDomain(LBL,X,bad)) :- _passed(sugar,set_baseDomain(LBL,X,E)), not _expression_wellformed(E).

%%%%%% statement atoms
_warning(atom(syntaxError),PRG,execution_declare(PRG)) :- _passed(defaultArgs,execution_declare(LBL,PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).
%%% TODO add bad for all exec outs


%%%%%% optimization atoms
_illformed(optimize_maximizeSum(LBL,E,X,P)) :- _passed(sugar,optimize_maximizeSum(LBL,E,X,P)), #false:
    _expression_wellformed(E),
    (number,_,_,_)=@pythonReify(P).
_illformed(optimize_precision(LBL,PREC,PRIO)) :- _passed(sugar,optimize_precision(LBL,PREC,PRIO)), #false:
    _expression_wellformed(PREC),
    (number,_,_,_)=@pythonReify(PRIO).
_warning(atom(syntaxError),(),DECL) :- _illformed(DECL).

%%%%%% preference atoms
_illformed(sugar,preference_holds(LBL,E,K)) :- _passed(sugar,preference_holds(LBL,E,K)), #false: _expression_wellformed(E), (number,_,_,_)=@pythonReify(K).
