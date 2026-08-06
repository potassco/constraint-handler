%%%%%%%%%%%%%%%%% _expression_wellformed
_expression_wfQuery(EXPR) :- _phase_active(wf_check), _expression(sugar,EXPR).
_expression_wellformed(bad) :- _phase_active(wf_check).
_expression_wellformed(python(CODE)) :- _expression_wfQuery(python(CODE)), true=@pythonIsString(CODE).
_expression_wellformed(pythonExtract(PSTMT,PEXPR)) :- _expression_wfQuery(pythonExtract(PSTMT,PEXPR)), true=@pythonIsString(PSTMT),true=@pythonIsString(PEXPR).
_expression_wellformed(val(T,V)) :- _expression_wfQuery(val(T,V)).
_expression_wellformed(variable(X)) :- _expression_wfQuery(variable(X)).
_expression_wellformed(operation(O,L)) :- _expression_wfQuery(operation(O,L)), true=@pythonIsList(L), _expression_wellformed(D) : D=@pythonListElements(L).
_expression_wellformed(EXPR) :- _expression_wfQuery(EXPR), true=@pythonIsTuple(EXPR), _expression_wellformed(D) : D=@pythonTupleElements(EXPR).
_expression_wellformed(lambda(ARGS,E)) :- _expression_wfQuery(lambda(ARGS,E)).
_warning(expression(syntaxError),(),"lambda checks unsupported") :- _expression_wfQuery(lambda(ARGS,E)). %TODO

% TODO: for operations, check that the operator is well-formed


_warning(expression(syntaxError),(),EXPR) :- _phase_active(wf_check), _expression(sugar,EXPR), not _expression_wellformed(EXPR).








%%%%%%%%%%%%%%%%% check if well-formed
_correction_expression(wf_check,EXPR,bad) :- _phase_active(wf_check), _expression(sugar,LBL,DECL,EXPR), not _expression_wellformed(EXPR).

_correction_number(wf_check,N,0) :- _phase_active(wf_check), _number(sugar,N), #false: (number,_,_,_)=@pythonReify(N).

%%%%%% statement atoms
_warning(atom(syntaxError),PRG,execution_declare(PRG)) :- _phase_active(wf_check), _passed(defaultArgs,LBL,execution_declare(PRG,STMT,INS,OUTS)),
    #false: _statement_wellformed(STMT), true=@pythonIsList(INS), true=@pythonIsList(OUTS).
%%% TODO add bad for all exec outs
